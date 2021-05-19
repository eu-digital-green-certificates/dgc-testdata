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
#
# References:
# https://ec.europa.eu/health/sites/health/files/ehealth/docs/trust-framework_interoperability_certificates_en.pdf
# https://ec.europa.eu/health/sites/health/files/ehealth/docs/vaccination-proof_interoperability-guidelines_en.pdf
#
# Dependencies:
# Python 3.9
# pip install wheel base45 jsonschema jsonref filecache cose pytest pyzbar Pillow python-dateutil

from pathlib import Path
from pytest import fixture
from glob import glob
from binascii import hexlify, unhexlify
from cbor2 import loads, CBORTag
from cose.algorithms import Es256, Ps256
from cose.keys import CoseKey
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN, KpKty, KpKeyOps
from cose.keys.keyops import VerifyOp
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.curves import P256
from cose.messages import Sign1Message
from cose.headers import KID
from base64 import b64decode
from base45 import b45decode
from datetime import datetime, timezone
from dateutil import parser
from json import load
from typing import Dict
from cryptography import x509
from cryptography.utils import int_to_bytes
from cryptography.x509 import ExtensionNotFound
from cryptography.x509.oid import SignatureAlgorithmOID
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.hashes import SHA256

from io import BytesIO
from PIL.Image import open as image_open
from pyzbar.pyzbar import decode as bar_decode
from os import path


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
QR_CODE = '2DCODE'
PREFIX = 'PREFIX'
BASE45 = 'BASE45'
COMPRESSED = 'COMPRESSED'


def pytest_generate_tests(metafunc):
    if "config_env" in metafunc.fixturenames:
        country_code = metafunc.config.getoption("country_code")
        file_name = metafunc.config.getoption("file_name")
        print(country_code, file_name)
        test_dir = path.dirname(path.abspath(__file__))
        test_files = glob(rf'{test_dir}\..\{country_code}\*\*\{file_name}.json', recursive=True)
        ids = [Path(*Path(test_file).parts[-4:]).as_posix() for test_file in test_files]
        metafunc.parametrize("config_env", test_files, indirect=True, ids=ids)


@fixture
def config_env(request):
    with open(request.param, encoding='utf8') as test_file:
        return load(test_file)


@fixture
def dgc(config_env: Dict) -> Sign1Message:
    if COSE in config_env.keys():
        cbor_bytes = unhexlify(config_env[COSE])
        cbor_object = loads(cbor_bytes)
        if isinstance(cbor_object, CBORTag):  # Tagged Cose Object
            decoded = Sign1Message.decode(cbor_bytes)
        else:  # Un-tagged Cose Object
            decoded = Sign1Message.from_cose_obj(cbor_object)
        return decoded
    # else:
    #     raise ValueError(f'Missing Test Data {COSE}')


@fixture
def dsc(config_env: Dict):
    if TEST_CONTEXT in config_env.keys() and CERTIFICATE in config_env[TEST_CONTEXT].keys():
        cert_code = config_env[TEST_CONTEXT][CERTIFICATE]
        x = y = e = n = None
        cert = x509.load_pem_x509_certificate(
            f'-----BEGIN CERTIFICATE-----\n{cert_code}\n-----END CERTIFICATE-----'.encode())

        fingerprint = cert.fingerprint(SHA256())
        keyid = fingerprint[0:8]

        # if cert.signature_algorithm_oid == SignatureAlgorithmOID.RSA_WITH_SHA256:
        if isinstance(cert.public_key(), rsa.RSAPublicKey):
            e = int_to_bytes(cert.public_key().public_numbers().e)
            n = int_to_bytes(cert.public_key().public_numbers().n)
        # elif cert.signature_algorithm_oid == SignatureAlgorithmOID.ECDSA_WITH_SHA256:
        elif isinstance(cert.public_key(), ec.EllipticCurvePublicKey):
            x = int_to_bytes(cert.public_key().public_numbers().x)
            y = int_to_bytes(cert.public_key().public_numbers().y)
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
    # else:
    #     raise ValueError(f'Missing Test Data {CERTIFICATE}')


def test_verification_check(config_env: Dict, dgc: Sign1Message, dsc):
    if EXPECTED_VERIFY in config_env[EXPECTED_RESULTS].keys():
        given_kid = None
        if COSE in config_env.keys():
            if KID in dgc.phdr.keys():
                given_kid = dgc.phdr[KID]
            else:
                given_kid = dgc.uhdr[KID]
        if config_env[EXPECTED_RESULTS][EXPECTED_VERIFY]:
            assert dsc[1] == given_kid
            dgc.key = dsc[0]
            assert dgc.verify_signature()
        elif dgc and dsc and dsc[0]:
            dgc.key = dsc[0]
            assert not all((dsc[1] == given_kid, dgc.verify_signature()))


def test_expiration_check(config_env: Dict, dgc: Sign1Message, dsc):
    dsc_not_valid_before, dsc_not_valid_after = dsc[3], dsc[4]
    if EXPECTED_EXPIRATION_CHECK not in config_env[EXPECTED_RESULTS].keys():
        return
    if TEST_CONTEXT in config_env.keys() and VALIDATION_CLOCK in config_env[TEST_CONTEXT].keys():
        validation_clock = parser.isoparse(config_env[TEST_CONTEXT][VALIDATION_CLOCK])
    else:
        validation_clock = datetime.utcnow()
    decoded_payload = loads(dgc.payload)
    assert {PAYLOAD_EXPIRY_DATE, PAYLOAD_ISSUE_DATE} <= decoded_payload.keys(), \
        f'COSE Payload is missing expiry date: {PAYLOAD_EXPIRY_DATE} and/or issue date: {PAYLOAD_ISSUE_DATE}.'
    dgc_expiry_date = datetime.fromtimestamp(decoded_payload[PAYLOAD_EXPIRY_DATE], tz=timezone.utc)
    dgc_issue_date = datetime.fromtimestamp(decoded_payload[PAYLOAD_ISSUE_DATE], tz=timezone.utc)
    if not validation_clock.tzinfo:  # if timezone is not provided, assume UTC
        validation_clock = validation_clock.replace(tzinfo=timezone.utc)
    if config_env[EXPECTED_RESULTS][EXPECTED_EXPIRATION_CHECK]:
        assert dsc_not_valid_before <= dgc_issue_date
        assert dgc_issue_date <= validation_clock
        assert validation_clock <= dgc_expiry_date
        assert dgc_expiry_date <= dsc_not_valid_after
    else:
        assert not all([dsc_not_valid_before <= dgc_issue_date,
                        dgc_issue_date <= validation_clock,
                        validation_clock <= dgc_expiry_date,
                        dgc_expiry_date <= dsc_not_valid_after])


def test_b45decode(config_env: Dict):
    if EXPECTED_B45DECODE in config_env[EXPECTED_RESULTS].keys() and {BASE45, COMPRESSED} <= config_env.keys():
        if config_env[EXPECTED_RESULTS][EXPECTED_B45DECODE]:
            assert (_get_compressed(config_env[BASE45]) == config_env[COMPRESSED].lower())
        else:
            assert not (_get_compressed(config_env[BASE45]) == config_env[COMPRESSED].lower())


def _get_compressed(base45_code):
    # noinspection PyBroadException
    try:
        return hexlify(b45decode(base45_code)).decode()
    except Exception:
        return None


def test_un_prefix(config_env: Dict):
    if EXPECTED_UN_PREFIX in config_env[EXPECTED_RESULTS].keys() and {BASE45, PREFIX} <= config_env.keys():
        if config_env[EXPECTED_RESULTS][EXPECTED_UN_PREFIX]:
            assert (f"HC1:{config_env[BASE45]}" == config_env[PREFIX])
        else:
            assert not (f"HC1:{config_env[BASE45]}" == config_env[PREFIX])


def test_picture_decode(config_env: Dict):
    if EXPECTED_PICTURE_DECODE in config_env[EXPECTED_RESULTS].keys() and {QR_CODE, PREFIX} <= config_env.keys():
        if config_env[EXPECTED_RESULTS][EXPECTED_PICTURE_DECODE]:
            assert (_get_code_content(config_env[QR_CODE]) == config_env[PREFIX])
        else:
            assert not (_get_code_content(config_env[QR_CODE]) == config_env[PREFIX])


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
