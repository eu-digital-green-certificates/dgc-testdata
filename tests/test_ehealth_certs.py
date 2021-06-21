#! /usr/bin/python
# ---license-start
# eu-digital-green-certificates / dgc-testdata
# ---
# Copyright (C) 2021 Qryptal Pte Ltd and all other contributors
# ---
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---license-end
#
# Created by Bhavin Sanghvi, Qryptal Pte Ltd, Singapore on 21 May 2021 4:00 PM
#
# Change Log:
# 21 Mar 2021 - Version 1.0.0 - Created by Qryptal Pte Ltd, Singapore - First version
#
# References:
# https://ec.europa.eu/health/sites/health/files/ehealth/docs/trust-framework_interoperability_certificates_en.pdf
# https://ec.europa.eu/health/sites/health/files/ehealth/docs/vaccination-proof_interoperability-guidelines_en.pdf
#
# Dependencies:
# Python 3.9
# pip install -r tests/requirements.txt
#
# Usage:
# To run all tests: pytest
# To run tests for a given country: pytest -C=<Country Code> . e.g. pytest -C=AT
# To run tests for a given test set: pytest -F=<Test Set Name> . e.g. pytest -C=AT -F=1


from base64 import b64decode
from binascii import hexlify, unhexlify
from csv import DictReader
from datetime import date, datetime, timezone
from glob import glob
from io import BytesIO
from json import load
from os import path
from pathlib import Path
from re import split
from traceback import format_exc
from typing import Dict
from PIL.Image import open as image_open
from base45 import b45decode
from cbor2 import loads, CBORTag
from cose.algorithms import Es256, Ps256
from cose.headers import KID
from cose.keys import CoseKey
from cose.keys.curves import P256
from cose.keys.keyops import VerifyOp
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN, KpKty, KpKeyOps
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.messages import Sign1Message
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.utils import int_to_bytes
from cryptography.x509 import ExtensionNotFound
from dateutil import parser
from filecache import filecache, DAY
from jsonref import load_uri
from jsonschema import validate as schema_validate
from pytest import fixture, skip, fail
from pytest import mark
from pyzbar.pyzbar import decode as bar_decode
from zlib import decompress

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
EXPECTED_KEY_USAGE = 'EXPECTEDKEYUSAGE'
TIMESTAMP_ISO8601_EXTENDED = "%Y-%m-%dT%H:%M:%S.%fZ"
TIMESTAMP_ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

CBOR = 'CBOR'
CERTIFICATE = 'CERTIFICATE'
COMPRESSED = 'COMPRESSED'
COSE = 'COSE'
JSON = 'JSON'
TEST_CONTEXT = 'TESTCTX'
VALIDATION_CLOCK = 'VALIDATIONCLOCK'
TWOD_CODE = '2DCODE'
PREFIX = 'PREFIX'
BASE45 = 'BASE45'
CONFIG_ERROR = 'CONFIG_ERROR'


@filecache(DAY)
def _get_hcert_schema():
    print('Loading HCERT schema ...')
    return load_uri('https://id.uvci.eu/DGC.schema.json')


def pytest_generate_tests(metafunc):
    if "config_env" in metafunc.fixturenames:
        country_code = metafunc.config.getoption("country_code")
        file_name = metafunc.config.getoption("file_name")
        print(country_code, file_name)
        test_dir = path.dirname(path.dirname(path.abspath(__file__)))
        test_files = glob(str(Path(test_dir, country_code, '*', '*', f'{file_name}.json')), recursive=True)
        # test_files = glob(f'{test_dir}\\..\\{country_code}\\*\\*\\{file_name}.json', recursive=True)
        ids = [Path(*Path(test_file).parts[-4:]).as_posix() for test_file in test_files]
        metafunc.parametrize("config_env", test_files, indirect=True, ids=ids)


@fixture(scope='session')
def known_issues():
    with open(Path(path.dirname(path.abspath(__file__)), 'known_issues.csv')) as know_issue_file:
        return {f'{known_issue["test_name"]}:{known_issue["country"]}:{known_issue["test_set"]}': known_issue["reason"]
                for known_issue in DictReader(know_issue_file)}  # test_name,country,test_set,reason


@fixture
def known_issue(request, known_issues: Dict[str, str]) -> str:
    test_function_name, country_code, *_, test_file_name, _, _ = tuple(split(r'[./\]\[]', request.node.name))
    if f'{test_function_name}:{country_code}:{test_file_name}' in known_issues.keys():
        return known_issues[f'{test_function_name}:{country_code}:{test_file_name}']
    if f'{test_function_name}:{country_code}:' in known_issues.keys():
        return known_issues[f'{test_function_name}:{country_code}:']
    if f':{country_code}:{test_file_name}' in known_issues.keys():
        return known_issues[f':{country_code}:{test_file_name}']
    if f':{country_code}:' in known_issues.keys():
        return known_issues[f':{country_code}:']
    return ""


@fixture
def config_env(request):
    # noinspection PyBroadException
    try:
        with open(request.param, encoding='utf8') as test_file:
            config_env = load(test_file)
            return config_env
    except Exception:
        return {CONFIG_ERROR: format_exc()}


@fixture(autouse=True)
def xfail_known_issues(request, known_issue: str):
    if known_issue:
        request.applymarker(mark.xfail(reason=known_issue))


# noinspection PyUnusedLocal
def _object_hook_e(decoder, value):
    return {k: v.astimezone(timezone.utc).strftime(TIMESTAMP_ISO8601_EXTENDED) if isinstance(v, (date, datetime)) else v
            for k, v in value.items()}


# noinspection PyUnusedLocal
def _object_hook(decoder, value):
    return {k: v.astimezone(timezone.utc).strftime(TIMESTAMP_ISO8601) if isinstance(v, (date, datetime)) else v
            for k, v in value.items()}


def _dgc(config_env: Dict) -> Sign1Message:
    if COSE in config_env.keys():
        cbor_bytes = unhexlify(config_env[COSE])
        cbor_object = loads(cbor_bytes, object_hook=_object_hook_e)
        if isinstance(cbor_object, CBORTag):  # Tagged Cose Object
            if isinstance(cbor_object.value, CBORTag):  # Double Tagged Cose Object
                decoded = Sign1Message.from_cose_obj(cbor_object.value.value)
            else:
                decoded = Sign1Message.decode(cbor_bytes)
        else:  # Un-tagged Cose Object
            decoded = Sign1Message.from_cose_obj(cbor_object)
        return decoded


def _dsc(config_env: Dict):
    if TEST_CONTEXT in config_env.keys() and CERTIFICATE in config_env[TEST_CONTEXT].keys():
        cert_code = config_env[TEST_CONTEXT][CERTIFICATE]
        x = y = e = n = None
        cert = x509.load_pem_x509_certificate(
            f'-----BEGIN CERTIFICATE-----\n{cert_code}\n-----END CERTIFICATE-----'.encode())

        fingerprint = cert.fingerprint(SHA256())
        keyid = fingerprint[0:8]

        if isinstance(cert.public_key(), rsa.RSAPublicKey):
            e = int_to_bytes(cert.public_key().public_numbers().e)
            n = int_to_bytes(cert.public_key().public_numbers().n)
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


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    else:
        return obj


def test_compression(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_COMPRESSION not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_COMPRESSION}')
    if not ({COSE, COMPRESSED} <= config_env.keys()):
        skip(f'Test dataset does not contain {COSE} and/or {COMPRESSED}')
    cbor_bytes = unhexlify(config_env[COSE])
    zip_bytes = unhexlify(config_env[COMPRESSED])
    if config_env[EXPECTED_RESULTS][EXPECTED_COMPRESSION]:
        decompressed_cbor_bytes = decompress(zip_bytes)
        assert decompressed_cbor_bytes == cbor_bytes
    else:
        # noinspection PyBroadException
        try:
            decompressed_cbor_bytes = decompress(zip_bytes)
        except Exception:
            return
        assert decompressed_cbor_bytes != cbor_bytes


def test_cose_schema(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_SCHEMA_VALIDATION not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_SCHEMA_VALIDATION}')
    if COSE not in config_env.keys():
        skip(f'Test dataset does not contain {COSE}')

    if config_env[EXPECTED_RESULTS][EXPECTED_SCHEMA_VALIDATION]:
        dgc = _dgc(config_env)
        cose_payload = loads(dgc.payload, object_hook=_object_hook_e)
        assert PAYLOAD_HCERT in cose_payload.keys()
        assert len(cose_payload[PAYLOAD_HCERT]) == 1
        assert 1 in cose_payload[PAYLOAD_HCERT].keys()
        hcert = cose_payload[PAYLOAD_HCERT][1]
        schema_validate(hcert, _get_hcert_schema())
        # assert len(set(hcert.keys()) & {'v', 'r', 't'}) == 1,
        # 'DGC adheres to schema but contains multiple certificates'
        assert len([key for key in hcert.keys() if key in ['v', 'r', 't']]) == 1, \
            'DGC adheres to schema but contains multiple certificates'


def test_cose_json(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_DECODE not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_DECODE}')
    if not ({COSE, JSON} <= config_env.keys()):
        skip(f'Test dataset does not contain {COSE} and/or {JSON}')
    dgc = _dgc(config_env)
    cose_payload_e = loads(dgc.payload, object_hook=_object_hook_e)
    cose_payload = loads(dgc.payload, object_hook=_object_hook)
    if config_env[EXPECTED_RESULTS][EXPECTED_DECODE]:
        assert PAYLOAD_HCERT in cose_payload.keys()
        assert len(cose_payload[PAYLOAD_HCERT]) == 1
        assert 1 in cose_payload[PAYLOAD_HCERT].keys()
        hcert = cose_payload[PAYLOAD_HCERT][1]
        hcert_e = cose_payload_e[PAYLOAD_HCERT][1]
        assert any([_ordered(hcert) == _ordered(config_env[JSON]),
                    _ordered(hcert_e) == _ordered(config_env[JSON])])


def test_cbor_json(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_VALID_JSON not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_VALID_JSON}')
    if not ({CBOR, JSON} <= config_env.keys()):
        skip(f'Test dataset does not contain {CBOR} and/or {JSON}')
    cbor_bytes = unhexlify(config_env[CBOR])
    cbor_object_e = loads(cbor_bytes, object_hook=_object_hook_e)
    cbor_object = loads(cbor_bytes, object_hook=_object_hook)
    if config_env[EXPECTED_RESULTS][EXPECTED_DECODE]:
        # assert PAYLOAD_HCERT in cbor_object.keys()
        if PAYLOAD_HCERT in cbor_object.keys():  # Hack in order to match different level of CBOR Payload
            cbor_object = cbor_object[PAYLOAD_HCERT][1]
        assert any([_ordered(cbor_object) == _ordered(config_env[JSON]),
                    _ordered(cbor_object_e) == _ordered(config_env[JSON])])
    else:
        assert _ordered(cbor_object) != _ordered(config_env[JSON])
        assert _ordered(cbor_object_e) != _ordered(config_env[JSON])


def test_cose_cbor(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_DECODE not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_DECODE}')
    if not ({CBOR, COSE} <= config_env.keys()):
        skip(f'Test dataset does not contain {CBOR} and/or {COSE}')
    cbor_bytes = unhexlify(config_env[CBOR])
    cbor_payload = loads(cbor_bytes, object_hook=_object_hook_e)
    dgc = _dgc(config_env)
    cose_payload = loads(dgc.payload, object_hook=_object_hook_e)

    if config_env[EXPECTED_RESULTS][EXPECTED_DECODE]:
        if PAYLOAD_HCERT not in cbor_payload.keys():  # Hack in order to match different level of CBOR Payload
            cose_payload = cose_payload[PAYLOAD_HCERT][1]
        assert _ordered(cbor_payload) == _ordered(cose_payload)
    else:
        assert not _ordered(cbor_payload) == _ordered(cose_payload)


def test_verification_check(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_VERIFY not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_VERIFY}')
    if COSE not in config_env.keys():
        skip(f'Test dataset does not contain {COSE}')
    if TEST_CONTEXT not in config_env.keys() or CERTIFICATE not in config_env[TEST_CONTEXT].keys():
        skip(f'Test dataset does not contain {TEST_CONTEXT} and/or {CERTIFICATE}')

    # noinspection PyBroadException
    try:
        dgc = _dgc(config_env)
        dsc = _dsc(config_env)
    except Exception:
        if config_env[EXPECTED_RESULTS][EXPECTED_VERIFY]:
            raise
        else:
            return

    given_kid = None
    if COSE in config_env.keys():
        if KID in dgc.phdr.keys():
            given_kid = dgc.phdr[KID]
        else:
            given_kid = dgc.uhdr[KID]
    if config_env[EXPECTED_RESULTS][EXPECTED_VERIFY]:
        assert given_kid == dsc[1], f'Invalid COSE kid value {given_kid}'
        dgc.key = dsc[0]
        assert dgc.verify_signature(), 'Could not validate DGC Signature'
    elif dgc and dsc and dsc[0]:
        dgc.key = dsc[0]
        assert not all((dsc[1] == given_kid, dgc.verify_signature()))


def test_expiration_check(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_EXPIRATION_CHECK not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_EXPIRATION_CHECK}')
    if COSE not in config_env.keys():
        skip(f'Test dataset does not contain {COSE}')
    if TEST_CONTEXT not in config_env.keys() or CERTIFICATE not in config_env[TEST_CONTEXT].keys():
        skip(f'Test dataset does not contain {TEST_CONTEXT} and/or {CERTIFICATE}')

    if TEST_CONTEXT in config_env.keys() and VALIDATION_CLOCK in config_env[TEST_CONTEXT].keys():
        validation_clock = parser.isoparse(config_env[TEST_CONTEXT][VALIDATION_CLOCK])
    else:
        validation_clock = datetime.utcnow()

    dsc = _dsc(config_env)
    dsc_not_valid_before, dsc_not_valid_after = dsc[3], dsc[4]
    dgc = _dgc(config_env)
    decoded_payload = loads(dgc.payload, object_hook=_object_hook_e)
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


def test_expected_key_usage(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_KEY_USAGE not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_KEY_USAGE}')
    if COSE not in config_env.keys():
        skip(f'Test dataset does not contain {COSE}')
    if TEST_CONTEXT not in config_env.keys() or CERTIFICATE not in config_env[TEST_CONTEXT].keys():
        skip(f'Test dataset does not contain {TEST_CONTEXT} and/or {CERTIFICATE}')

    dsc = _dsc(config_env)
    dsc_supported_operations = dsc[2]
    dgc = _dgc(config_env)
    cose_payload = loads(dgc.payload, object_hook=_object_hook_e)
    assert PAYLOAD_HCERT in cose_payload.keys()
    assert len(cose_payload[PAYLOAD_HCERT]) == 1
    assert 1 in cose_payload[PAYLOAD_HCERT].keys()
    hcert = cose_payload[PAYLOAD_HCERT][1]
    assert len([key for key in hcert.keys() if key in ['v', 'r', 't']]) == 1, \
        'DGC adheres to schema but contains multiple certificates'
    # assert len(set(hcert.keys()) & {'v', 'r', 't'}) == 1, \
    #     'DGC adheres to schema but contains multiple certificates of different types'
    hcert_type = (set(hcert.keys()) & {'v', 'r', 't'}).pop()

    if config_env[EXPECTED_RESULTS][EXPECTED_KEY_USAGE] and dsc_supported_operations:
        assert (dsc_supported_operations & CERT_VALIDITY_MAP[hcert_type]), \
            f'Given DSC is not valid to sign HCERT Type: {hcert_type}'
    elif dsc_supported_operations:
        assert not (dsc_supported_operations & CERT_VALIDITY_MAP[hcert_type]), \
            f'Given DSC is valid to sign HCERT Type: {hcert_type}'
    elif not config_env[EXPECTED_RESULTS][EXPECTED_KEY_USAGE]:
        fail(f'Given DSC is valid to sign HCERT Type: {hcert_type}')


def test_b45decode(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_B45DECODE not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_B45DECODE}')
    if not ({BASE45, COMPRESSED} <= config_env.keys()):
        skip(f'Test dataset does not contain {BASE45} and/or {COMPRESSED}')
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
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_UN_PREFIX not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_UN_PREFIX}')
    if not ({BASE45, PREFIX} <= config_env.keys()):
        skip(f'Test dataset does not contain {BASE45} and/or {PREFIX}')
    if config_env[EXPECTED_RESULTS][EXPECTED_UN_PREFIX]:
        assert (f"HC1:{config_env[BASE45]}" == config_env[PREFIX])
    else:
        assert not (f"HC1:{config_env[BASE45]}" == config_env[PREFIX])


def test_picture_decode(config_env: Dict):
    if CONFIG_ERROR in config_env.keys():
        fail(f'Config Error: {config_env[CONFIG_ERROR]}')
    if EXPECTED_PICTURE_DECODE not in config_env[EXPECTED_RESULTS].keys():
        skip(f'Test not requested: {EXPECTED_PICTURE_DECODE}')
    if not ({TWOD_CODE, PREFIX} <= config_env.keys()):
        skip(f'Test dataset does not contain {TWOD_CODE} and/or {PREFIX}')

    # noinspection PyBroadException
    try:
        code_content = _get_code_content(config_env[TWOD_CODE])
    except Exception:
        if config_env[EXPECTED_RESULTS][EXPECTED_PICTURE_DECODE]:
            raise
        else:
            return
    if config_env[EXPECTED_RESULTS][EXPECTED_PICTURE_DECODE]:
        assert (code_content == config_env[PREFIX])
    else:
        assert not (code_content == config_env[PREFIX])


def _get_code_content(base64_image):
    b = b64decode(base64_image)
    with BytesIO(b) as f:
        with image_open(f) as image:
            dec = bar_decode(image)[0]
    return dec.data.decode()
