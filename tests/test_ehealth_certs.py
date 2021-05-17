#! /usr/bin/python
#
# Copyright 2021 Qryptal Pte Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Change Log:
# Version 1.0.0 - Created by Qryptal Pte Ltd, Singapore - First version
# Version 1.0.1 - Modified by Qryptal Pte Ltd, Singapore - Support Key Validity using VALID_FROM_ts and VALID_UNTIL_ts
#
# References:
# https://ec.europa.eu/health/sites/health/files/ehealth/docs/trust-framework_interoperability_certificates_en.pdf
# https://ec.europa.eu/health/sites/health/files/ehealth/docs/vaccination-proof_interoperability-guidelines_en.pdf
#
# Dependencies:
# Python 3.9
# pip install wheel base45 jsonschema jsonref filecache cose pytest pyzbar Pillow python-dateutil
# Usage Examples:
# python ehealth_cert_verification.py -t "<<Secured Code Payload>>"
# python ehealth_cert_verification.py -k "<<Key File>>" -t "<<Secured Code Payload>>"

from csv import DictWriter
from glob import glob
from binascii import hexlify, unhexlify
from cbor2 import loads, CBORTag
from cose.algorithms import Es256, Ps256
from cose.keys import CoseKey
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN, KpKty, KpKeyOps
from cose.keys.keyops import VerifyOp
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.curves import P256
from cose.messages import Sign1Message, CoseMessage
from cose.headers import KID
from base64 import b64encode, b64decode
from base45 import b45decode
from datetime import datetime, timezone
from dateutil import parser
from filecache import filecache, DAY
from zlib import decompress
from json import load
from jsonschema import validate, ValidationError
from jsonref import load_uri
from argparse import Namespace
from pprint import pprint
from typing import Dict, List
from cryptography import x509
from cryptography.utils import int_to_bytes
from cryptography.x509 import ExtensionNotFound
from cryptography.x509.oid import SignatureAlgorithmOID
from cryptography.hazmat.primitives.hashes import SHA256

from io import BytesIO
from PIL.Image import open as image_open
from pyzbar.pyzbar import decode as bar_decode

VERSION = '1.1.0'
VALID_FROM, VALID_UNTIL = 'VALID_FROM_ts', 'VALID_UNTIL_ts'
KID_MAP = 'KID_map'
KTY, CURVE, ALG = 'KTY', 'CURVE', 'ALG'
X_HEX, Y_HEX = 'X_hex', 'Y_hex'
PAYLOAD_ISSUER, PAYLOAD_ISSUE_DATE, PAYLOAD_EXPIRY_DATE, PAYLOAD_HCERT = 1, 6, 4, -260

CERT_VALIDITY_MAP = {'t': {'1.3.6.1.4.1.0.1847.2021.1.1', '1.3.6.1.4.1.1847.2021.1.1'},
                     'v': {'1.3.6.1.4.1.0.1847.2021.1.2', '1.3.6.1.4.1.1847.2021.1.2'},
                     'r': {'1.3.6.1.4.1.0.1847.2021.1.3', '1.3.6.1.4.1.1847.2021.1.3'}}

EXPECTED_RESULTS = 'EXPECTEDRESULTS'
EXPECTED_PICTURE_DECODE = 'EXPECTEDPICTUREDECODE'
EXPECTED_UN_PREFIX = 'EXPECTEDUNPREFIX'
EXPECTED_B45DECODE = 'EXPECTEDB45DECODE'
EXPECTED_EXPIRATION_CHECK = 'EXPECTEDEXPIRATIONCHECK'
EXPECTED_VERIFY = 'EXPECTEDVERIFY'
EXPECTED_DECODE = 'EXPECTEDDECODE'
EXPECTED_VALID_JSON = 'EXPECTEDVALIDJSON'
EXPECTED_SCHEMA_VALIDATION = 'EXPECTEDSCHEMAVALIDATION'
EXPECTED_COMPRESSION = 'EXPECTEDCOMPRESSION'

VALIDATION_CLOCK = 'VALIDATIONCLOCK'
COSE = 'COSE'
TEST_CONTEXT = 'TESTCTX'
CERTIFICATE = 'CERTIFICATE'

CSV_COLUMN_ORDER = ['test_set',
                    'error',
                    EXPECTED_PICTURE_DECODE,
                    EXPECTED_UN_PREFIX,
                    EXPECTED_B45DECODE,
                    EXPECTED_EXPIRATION_CHECK,
                    EXPECTED_VERIFY]


@filecache(DAY)
def get_hcert_schema():
    print('Loading HCERT schema ...')
    return load_uri('https://id.uvci.eu/DGC.schema.json')


def validate_code(params: Namespace):
    if not params.input.startswith('HC1:'):
        raise Exception('Error: Not a valid ehealth cert payload')

    b45string = params.input[4:]
    zip_bytes = b45decode(b45string)
    cbor_bytes = decompress(zip_bytes)
    cbor_object = loads(cbor_bytes)
    # print(loads(cbor_bytes).keys())
    if isinstance(cbor_object, CBORTag):  # Tagged Cose Object
        decoded = CoseMessage.decode(cbor_bytes)
    else:  # Un-tagged Cose Object
        decoded = Sign1Message.from_cose_obj(cbor_object)

    if KID in decoded.phdr.keys():
        key_id = b64encode(decoded.phdr[KID]).decode()
    elif KID in decoded.uhdr.keys():
        key_id = b64encode(decoded.uhdr[KID]).decode()
    else:
        raise Exception('Error: Could not identify public key for verification. KID is missing from the header!')

    with open(params.dsc_certs) as json_file:
        dsc_certs: Dict = load(json_file)

    if key_id in dsc_certs.keys():
        eligible_certs: List = dsc_certs[key_id]
    else:
        raise Exception(f'Error: Verification certificate with Key ID : {key_id} is missing from {params.dsc_certs}!')

    for cert in eligible_certs:
        x = y = e = n = None
        cert = x509.load_pem_x509_certificate(
            f'-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----'.encode())
        pub = cert.public_key().public_numbers()
        if cert.signature_algorithm_oid == SignatureAlgorithmOID.RSA_WITH_SHA256:
            e = int_to_bytes(pub.e)
            n = int_to_bytes(pub.n)
        elif cert.signature_algorithm_oid == SignatureAlgorithmOID.ECDSA_WITH_SHA256:
            x = int_to_bytes(pub.x)
            y = int_to_bytes(pub.y)
        else:
            raise Exception(
                f'Unsupported Certificate Algorithm: {cert.signature_algorithm_oid} for verification.'
            )
        try:
            dsc_supported_operations = {eku.dotted_string for eku in
                                        cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value}
        except ExtensionNotFound:
            dsc_supported_operations = set()
        dsc_not_valid_before, dsc_not_valid_after = cert.not_valid_before, cert.not_valid_after

        if x and y:
            decoded.key = CoseKey.from_dict(
                {
                    KpKeyOps: [VerifyOp],
                    KpKty: KtyEC2,
                    EC2KpCurve: P256,  # Ought o be pk.curve - but the two libs clash
                    KpAlg: Es256,  # ECDSA using P-256 and SHA-256
                    EC2KpX: x,
                    EC2KpY: y,
                }
            )
        elif e and n:
            decoded.key = CoseKey.from_dict(
                {
                    KpKeyOps: [VerifyOp],
                    KpKty: KtyRSA,
                    KpAlg: Ps256,  # RSASSA-PSS using SHA-256 and MGF1 with SHA-256
                    RSAKpE: e,
                    RSAKpN: n,
                }
            )

        if not decoded.verify_signature():
            continue

        decoded_payload = loads(decoded.payload)
        # dgc_issuer = decoded_payload[PAYLOAD_ISSUER] if PAYLOAD_ISSUER in decoded_payload.keys() else None
        dgc_issue_date = datetime.utcfromtimestamp(decoded_payload[PAYLOAD_ISSUE_DATE])
        dgc_expiry_date = datetime.utcfromtimestamp(decoded_payload[PAYLOAD_EXPIRY_DATE])
        hcert_collection: Dict[Dict] = decoded_payload[PAYLOAD_HCERT]

        if dgc_issue_date < dsc_not_valid_before or dgc_issue_date > dsc_not_valid_after:
            raise Exception('Error: DGC signed using the key with issue date outside of its validity period.')
        if dgc_expiry_date < dsc_not_valid_before or dgc_expiry_date > dsc_not_valid_after:
            raise Exception('Error: DGC signed using the key with expiry date outside of its validity period.')
        if dgc_expiry_date < datetime.utcnow():
            print(f'Warning: DGC validity is expired on {dgc_expiry_date}.')

        for hcert in hcert_collection.values():  # type: Dict
            try:
                validate(hcert, get_hcert_schema())
            except ValidationError:
                raise Exception(f'Error: Invalid HCERT Payload: {hcert}')
            if len(set(hcert.keys()) & {'v', 'r', 't'}) > 1:
                raise Exception(f'Error: DGC adheres to schema but contains multiple certificates')
            hcert_type = (set(hcert.keys()) & {'v', 'r', 't'}).pop()
            if dsc_supported_operations and not (dsc_supported_operations & CERT_VALIDITY_MAP[hcert_type]):
                raise Exception(f'Error: Given DSC is not valid to sign HCERT Type: {hcert_type}')
            pprint(hcert)

        pprint('Message Validation Successful!')
        return

    raise Exception('faulty sig')


def test_one():
    test_set = r'.\..\ES\2DCode\raw\101.json'
    test_summary = []
    _set_test(test_set, test_summary)
    csv_file = 'test_one.csv'
    with open(csv_file, 'w', newline='') as output_file:
        dict_writer = DictWriter(output_file, CSV_COLUMN_ORDER, extrasaction='ignore')
        dict_writer.writeheader()
        dict_writer.writerows(test_summary)
    print('Test passed!')


def test_all():
    print('test_all started...')
    test_summary = []
    test_sets = glob('.\\..\\**\\*.json', recursive=True)
    test_count = 0
    for test_set in test_sets:
        _set_test(test_set, test_summary)
        test_count += 1
        # if test_count > 250:
        #     break
    csv_file = 'test_summary.csv'
    with open(csv_file, 'w', newline='') as output_file:
        dict_writer = DictWriter(output_file, CSV_COLUMN_ORDER, extrasaction='ignore')
        dict_writer.writeheader()
        dict_writer.writerows(test_summary)
    print('Test passed!')


def _set_test(test_set, test_summary):
    with open(test_set, encoding='utf8') as test_file:
        # print(f'Testing {test_set}')
        test_result = {"test_set": test_set, "error": ""}
        test_result = _dgc_test(load(test_file), test_result)
        test_summary.append(test_result)


def _dgc_test(dgc_example: Dict, test_result: Dict):
    if EXPECTED_RESULTS in dgc_example.keys():
        _picture_decode_test(dgc_example, test_result)
        _un_prefix_test(dgc_example, test_result)
        _b45decode_test(dgc_example, test_result)
        if {COSE, TEST_CONTEXT} <= dgc_example.keys() and CERTIFICATE in dgc_example[TEST_CONTEXT].keys():
            try:
                cose_object = _get_cose_object(dgc_example[COSE])
                decoded_payload = loads(cose_object.payload)
                key, keyid, dsc_supported_operations, dsc_not_valid_before, dsc_not_valid_after = \
                    _get_cert(dgc_example[TEST_CONTEXT][CERTIFICATE])
                cose_object.key = key
                _expiration_check(dgc_example, decoded_payload, dsc_not_valid_before, dsc_not_valid_after, test_result)
                _verification_check(dgc_example, cose_object, keyid, test_result)
            except Exception as ex:
                test_result['error'] += repr(ex)
        else:
            test_result['error'] += f'Missing Test Data {COSE} or {TEST_CONTEXT},'
    return test_result


def _verification_check(dgc_example: Dict, cose_object: Sign1Message, keyid, test_result: Dict):
    if EXPECTED_VERIFY in dgc_example[EXPECTED_RESULTS].keys():
        test_result[EXPECTED_VERIFY] = f"{dgc_example[EXPECTED_RESULTS][EXPECTED_VERIFY]}"
        if KID in cose_object.phdr.keys():
            given_kid = cose_object.phdr[KID]
        else:
            given_kid = cose_object.uhdr[KID]
        result = 'Pass' if (cose_object.verify_signature() and keyid == given_kid) == \
                           dgc_example[EXPECTED_RESULTS][EXPECTED_VERIFY] else 'Failed'
        test_result[EXPECTED_VERIFY] += f':{result}'


def _expiration_check(dgc_example: Dict, decoded_payload: Dict, dsc_not_valid_before: datetime,
                      dsc_not_valid_after: datetime, test_result: Dict):
    if EXPECTED_EXPIRATION_CHECK in dgc_example[EXPECTED_RESULTS].keys():
        test_result[EXPECTED_EXPIRATION_CHECK] = f"{dgc_example[EXPECTED_RESULTS][EXPECTED_EXPIRATION_CHECK]}"
        if VALIDATION_CLOCK in dgc_example[TEST_CONTEXT].keys():
            if {PAYLOAD_EXPIRY_DATE, PAYLOAD_ISSUE_DATE} <= decoded_payload.keys():
                dgc_expiry_date = datetime.fromtimestamp(decoded_payload[PAYLOAD_EXPIRY_DATE], tz=timezone.utc)
                dgc_issue_date = datetime.fromtimestamp(decoded_payload[PAYLOAD_ISSUE_DATE], tz=timezone.utc)
                validation_clock = parser.isoparse(dgc_example[TEST_CONTEXT][VALIDATION_CLOCK])
                if not validation_clock.tzinfo:
                    validation_clock = validation_clock.replace(tzinfo=timezone.utc)
                result = 'Pass' if (dsc_not_valid_before <= dgc_issue_date <= validation_clock <= dgc_expiry_date <=
                                    dsc_not_valid_after) == dgc_example[EXPECTED_RESULTS][EXPECTED_EXPIRATION_CHECK] \
                    else 'Failed'
            else:
                result = 'Failed'
                test_result['error'] += \
                    f'Cose payload does not contain key {PAYLOAD_EXPIRY_DATE} and/or {PAYLOAD_ISSUE_DATE},'
            test_result[EXPECTED_EXPIRATION_CHECK] += f':{result}'
        else:
            test_result[EXPECTED_EXPIRATION_CHECK] += f':NotRun'
            test_result['error'] += f'Missing Test Data {VALIDATION_CLOCK},'


def _get_cert(cert_code):
    x = y = e = n = None
    cert = x509.load_pem_x509_certificate(
        f'-----BEGIN CERTIFICATE-----\n{cert_code}\n-----END CERTIFICATE-----'.encode())
    pub = cert.public_key().public_numbers()
    fingerprint = cert.fingerprint(SHA256())
    keyid = fingerprint[0:8]

    if cert.signature_algorithm_oid == SignatureAlgorithmOID.RSA_WITH_SHA256:
        e = int_to_bytes(pub.e)
        n = int_to_bytes(pub.n)
    elif cert.signature_algorithm_oid == SignatureAlgorithmOID.ECDSA_WITH_SHA256:
        x = int_to_bytes(pub.x)
        y = int_to_bytes(pub.y)
    else:
        raise Exception(
            f'Unsupported Certificate Algorithm: {cert.signature_algorithm_oid} for verification.'
        )
    try:
        dsc_supported_operations = {eku.dotted_string for eku in
                                    cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value}
    except ExtensionNotFound:
        dsc_supported_operations = set()
    dsc_not_valid_before = cert.not_valid_before.replace(tzinfo=timezone.utc)
    dsc_not_valid_after = cert.not_valid_after.replace(tzinfo=timezone.utc)
    key = None
    if x and y:
        key = CoseKey.from_dict(
            {
                KpKeyOps: [VerifyOp],
                KpKty: KtyEC2,
                EC2KpCurve: P256,  # Ought o be pk.curve - but the two libs clash
                KpAlg: Es256,  # ECDSA using P-256 and SHA-256
                EC2KpX: x,
                EC2KpY: y,
            }
        )
    elif e and n:
        key = CoseKey.from_dict(
            {
                KpKeyOps: [VerifyOp],
                KpKty: KtyRSA,
                KpAlg: Ps256,  # RSASSA-PSS using SHA-256 and MGF1 with SHA-256
                RSAKpE: e,
                RSAKpN: n,
            }
        )
    return key, keyid, dsc_supported_operations, dsc_not_valid_before, dsc_not_valid_after


def _get_cose_object(cose_code: str):
    cbor_bytes = unhexlify(cose_code)
    cbor_object = loads(cbor_bytes)
    # print(loads(cbor_bytes).keys())
    if isinstance(cbor_object, CBORTag):  # Tagged Cose Object
        decoded = CoseMessage.decode(cbor_bytes)
    else:  # Un-tagged Cose Object
        decoded = Sign1Message.from_cose_obj(cbor_object)
    return decoded


def _b45decode_test(dgc_example: Dict, test_result: Dict):
    if EXPECTED_B45DECODE in dgc_example[EXPECTED_RESULTS].keys():
        test_result[EXPECTED_B45DECODE] = f"{dgc_example[EXPECTED_RESULTS][EXPECTED_B45DECODE]}"
        if {'BASE45', 'COMPRESSED'} <= dgc_example.keys():
            result = 'Pass' if (_get_compressed(dgc_example['BASE45']) == dgc_example['COMPRESSED'].lower()) \
                               == dgc_example[EXPECTED_RESULTS][EXPECTED_B45DECODE] else 'Failed'
            test_result[EXPECTED_B45DECODE] += f':{result}'
        else:
            test_result[EXPECTED_B45DECODE] += f':NotRun'
            test_result['error'] += 'Missing Test Data BASE45 or COMPRESSED,'


def _get_compressed(base45_code):
    # noinspection PyBroadException
    try:
        return hexlify(b45decode(base45_code)).decode()
    except Exception:
        return None


def _un_prefix_test(dgc_example: Dict, test_result: Dict):
    if EXPECTED_UN_PREFIX in dgc_example[EXPECTED_RESULTS].keys():
        test_result[EXPECTED_UN_PREFIX] = f"{dgc_example[EXPECTED_RESULTS][EXPECTED_UN_PREFIX]}"
        if {'BASE45', 'PREFIX'} <= dgc_example.keys():

            result = 'Pass' if (f"HC1:{dgc_example['BASE45']}" == dgc_example['PREFIX']) == \
                               dgc_example[EXPECTED_RESULTS][EXPECTED_UN_PREFIX] else 'Failed'
            test_result[EXPECTED_UN_PREFIX] += f':{result}'
        else:
            test_result[EXPECTED_UN_PREFIX] += f':NotRun'
            test_result['error'] += 'Missing Test Data BASE45 or PREFIX,'


def _picture_decode_test(dgc_example: Dict, test_result: Dict):
    if EXPECTED_PICTURE_DECODE in dgc_example[EXPECTED_RESULTS].keys():
        test_result[EXPECTED_PICTURE_DECODE] = f"{dgc_example[EXPECTED_RESULTS][EXPECTED_PICTURE_DECODE]}"
        if {'2DCODE', 'PREFIX'} <= dgc_example.keys():
            result = 'Pass' if (_get_code_content(dgc_example['2DCODE']) == dgc_example['PREFIX']) \
                                == dgc_example[EXPECTED_RESULTS][EXPECTED_PICTURE_DECODE] else 'Fail'
            test_result[EXPECTED_PICTURE_DECODE] += f':{result}'
        else:
            test_result[EXPECTED_PICTURE_DECODE] += f':NotRun'
            test_result['error'] += 'Missing Test Data 2DCODE or PREFIX,'
    else:
        test_result[EXPECTED_PICTURE_DECODE] = ''


def _get_code_content(base64_image):
    # noinspection PyBroadException
    try:
        b = b64decode(base64_image)
        with BytesIO(b) as f:
            with image_open(f) as image:
                dec = bar_decode(image)[0]
        return dec.data.decode()
    except Exception:
        return None
