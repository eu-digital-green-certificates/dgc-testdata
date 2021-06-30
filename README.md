<h1 align="center">
 EU Digital COVID Certificate: Test Data Repository for Test Automation
</h1>

<p align="center">
    <a href="#about">About</a> •
    <a href="#testing--status">Testing & Status</a> •
    <a href="#2d-code">2D Code</a> •
    <a href="#how-to-contribute">How to Contribute</a> •
    <a href="#licensing">Licensing</a>
</p>

## About

To automate the generation and validation tests of COSE/CBOR Codes and its base45/2D Code representations, a lot of data has to be collected to ensure the variance of the tests. This repository was established to collect a lot of different test data and related test cases of different member states in a standardized manner. Each member state can generate a folder in this section.

## Testing & Status

- If you found any problems, please create an [Issue](/../../issues).
- Please make sure to review the issues to see if any other members states found issues with your provided test data.

## 2D Code

### Test Procedure

The test procedure has the following steps:

1. Load RAW Data File X
2. Apply all test and validation rules to File X (from all countries).
3. If one rule fails, the RAW Data File X is highlighted with the related Validation Rule/TestName Fail Status.

**Note**: If some of the "EXPECTEDRESULT" values are not present, the steps in the tests run can be skipped. The related data can be removed then as well. E.g. if just a "Expiring" test is constructed, the "EXPECTEDEXPIRATIONCHECK" value can be set together with an "COSE" and "VALIDATIONCLOCK" raw object. All other fields are then not necessary.

| Field           | Definition                                                 |
|-----------------|------------------------------------------------------------|
| JSON            | The JSON-encoding of the Digital Green Certificate payload |
| CBOR            | The CBOR-encoding of the Digital Green Certificate payload |
| COSE            | The CWT defined by the hCert Spec.                         |
| COMPRESSED      | A CWT compressed by zLib                                   |
| BASE45          | The base45 encoding of the compression.                    |
| PREFIX          | The base45 string concatenated with the Prefix (HC1 etc.)  |
| 2DCODE          | The base64 encoded PNG of a QR Code.                       |
| TESTCTX         | Testcontext with context information of the raw data.      |
| EXPECTEDRESULTS | A list of expected results to the testdata.                |

Possible boolean variables set in `EXPECTEDRESULTS`:
- `EXPECTEDSCHEMAVALIDATION`: Decoded data is valid according to dgc-schema
- `EXPECTEDDECODE`: Data from input in `CBOR` can be decoded, and the contents match input from `JSON`
- `EXPECTEDVERIFY`: Data from input in `COSE` can be cryptographically verified, with signer's certificate from `TESTCTX.CERTIFICATE`
- `EXPECTEDUNPREFIX`: Data from input in `PREFIX` can be decoded, i.e. contains a valid prefix (e.g. `HC1:` for now), and is equal to input in `BASE45`
- `EXPECTEDVALIDJSON`: Data from input (i.e. `2DCODE` or `PREFIX`) can be decoded (whole chain), and the contents match input from `JSON`
- `EXPECTEDCOMPRESSION`: Data from input in `COMPRESSED` can be decompressed (with ZLIB), and matches input in `COSE`
- `EXPECTEDB45DECODE`: Data from input in `BASE45` can be decoded (from Base45), and matches input in `COMPRESSED`
- `EXPECTEDPICTUREDECODE`: Data from input in `2DCODE` can be decoded (from Base64-encoded PNG), and matches input in `PREFIX`
- `EXPECTEDEXPIRATIONCHECK`: Data from input is valid when verifying at the moment defined in `TESTCTX.VALIDATIONCLOCK`
- `EXPECTEDKEYUSAGE`: Data from input in `COSE` can be verified, and the key usage (defined by the OIDs) from `TESTCTX.CERTIFICATE` matches the content (i.e. it is a test statement, vaccination statement, or recovery statement)

For all variables above:
- When not set, this specific validation step is not tested in this input file
- When set to `true`, this validation step should succeed
- When set to `false`, this validation step should fail

### Gateway

To indidcate which gateway environment is available, the test data context should contain: **GATEWAY-ENV**:**Array**

Example:

`GATEWAY-ENV`:["ACC", "TST"]

**Note:** Prod Keys should not be uploaded.

#### Code Generation

| Test Number | Test| Mandatory Fields|Mandatory Test Context Fields| Variable|
| :--- | :--- | :--- | :--- | :--- |
|1            | Load RAW File and load JSON Object, validate against the referenced JSON schema in the test context(SCHEMA field). |JSON| SCHEMA| EXPECTEDVALIDOBJECT|
|2            | Create CBOR from JSON Object. Validate against the CBOR content in the RAW File. See note 2 below. |JSON, CBOR||EXPECTEDENCODE|

**NOTE**: DESCRIPTION, VERSION are mandatory for all tests.

**NOTE 2**: CBOR objects that are maps (i.e., the Digital Green Certificate), have an undefined order. This means that the actual encodings between two objects containing the same elements may differ since the ordering may be different. Therefore the validation can not be as simple as comparing two byte arrays against each other. The best method is to decode both elements that are to be compared with the same decoder, encode both objects with the same encoder, and then compare.

#### Code Validation

| Test Number | Test                                                                                                         | Mandatory Fields | Mandatory Test Context Fields | Variable                 |
| :---        | :---                                                                                                         | :---             | :---                          | :---                     |
| 1           | Load the picture and extract the prefixed BASE45content.                                                     | PREFIX , 2DCode  |                               | EXPECTEDPICTUREDECODE    |
| 2           | Load Prefix Object from RAW Content and remove the prefix. Validate against the BASE45 raw content.          | PREFIX, BASE45   |                               | EXPECTEDUNPREFIX         |
| 3           | Decode the BASE45 RAW Content and validate the COSE content against the RAW content.                         | BASE45, COSE     |                               | EXPECTEDB45DECODE        |
| 4           | Check the EXP Field for expiring against the **VALIDATIONCLOCK** time.                                       | COSE             | VALIDATIONCLOCK               | EXPECTEDEXPIRATIONCHECK  |
| 5           | Verify the signature of the COSE Object against the JWK Public Key.                                          | COSE             | JWK                           | EXPECTEDVERIFY           |
| 6           | Extract the CBOR content and validate the CBOR content against the RAW CBOR content field. See note 2 below. | COSE,CBOR        |                               | EXPECTEDDECODE           |
| 7           | Transform CBOR into JSON and validate against the RAW JSON content. See note 3 below.                        | CBOR,JSON        |                               | EXPECTEDVALIDJSON        |
| 8           | Validate the extracted JSON against the schema defined in the test context.                                  | CBOR,JSON        | SCHEMA                        | EXPECTEDSCHEMAVALIDATION |
| 9           | The value given in COMPRESSED has to be decompressed by zlib and must match to the value given in COSE| COSE,COMPRESSED||EXPECTEDCOMPRESSION|

**NOTE**: DESCRIPTION, VERSION are mandatory for all tests.

**NOTE 2**: CBOR objects that are maps (i.e., the Digital Green Certificate), have an undefined order. This means that the actual encodings between two objects containing the same elements may differ since the ordering may be different. Therefore the validation can not be as simple as comparing two byte arrays against each other. The best method is to decode both elements that are to be compared with the same decoder, encode both objects with the same encoder, and then compare.

**NOTE 3**: As CBOR objects, JSON objects are not ordered, and a plain string comparison of two objects can not be performed.

### File Structure
/schema/**[semver]**.json <br>
/COMMON/2DCode/raw/**[Number]**.json <br>
**[COUNTRY]**/2DCode/raw/**[Number]**.json <br>

### Variables

COUNTRY is defined as the country code by ISO 3166.

Number must be a unique number by country/type.

### JSON Schema

A number which identifies the used schema (used in the RAW Data).

### RAW Content



The JSON Content under RAW is defined as:
```
{
   "JSON": **JSON OBJECT**,
   "CBOR": **CBOR (hex encoded)**,
   "COSE": **COSE (hex encoded)**,
   "COMPRESSED": **COMPRESSED (hex encoded)**,
   "BASE45": **BASE45 Encoded compressed COSE**,
   "PREFIX": **BASE45 Encoded compressed COSE with Prefix HC(x):**,
   "2DCODE": **BASE64 Encoded PNG**,
   "TESTCTX":{
       "VERSION": **integer**,
       "SCHEMA": **string (USED SCHEMA, semver)**,
       "CERTIFICATE": **BASE64** ,
       "VALIDATIONCLOCK": **Timestamp**, (https://docs.jsonata.org/date-time-functions ISO8601)
       "DESCRIPTION": **string**,
       "GATEWAY-ENV":**Array**
   },
   "EXPECTEDRESULTS": {
       "EXPECTEDVALIDOBJECT": **boolean**,
       "EXPECTEDSCHEMAVALIDATION": **boolean**,
       "EXPECTEDENCODE": **boolean**,
       "EXPECTEDDECODE": **boolean**,
       "EXPECTEDVERIFY": **boolean**,
       "EXPECTEDCOMPRESSION": **boolean**,
       "EXPECTEDKEYUSAGE": **boolean**,
       "EXPECTEDUNPREFIX": **boolean**,
       "EXPECTEDVALIDJSON": **boolean**,
       "EXPECTEDB45DECODE": **boolean**,
       "EXPECTEDPICTUREDECODE": **boolean**,
       "EXPECTEDEXPIRATIONCHECK": **boolean**,
    }
}
 ```
Example:
```
{
    "JSON": {
        "ver": "1.0.0",
        "nam": {
            "fn": "Musterfrau-Gößinger",
            "fnt": "MUSTERFRAU<GOESSINGER",
            "gn": "Gabriele",
            "gnt": "GABRIELE"
        },
        "dob": "1998-02-26",
        "v": [
            {
                "tg": "840539006",
                "vp": "1119305005",
                "mp": "EU/1/20/1528",
                "ma": "ORG-100030215",
                "dn": 1,
                "sd": 2,
                "dt": "2021-02-18",
                "co": "AT",
                "is": "BMSGPK Austria",
                "ci": "urn:uvci:01:AT:10807843F94AEE0EE5093FBC254BD813P"
            }
        ]
    },
    "CBOR": "bf6376657265312e302e30636e616dbf62666e754d7573746572667261752d47c3b6c39f696e67657263666e74754d5553544552465241553c474f455353494e47455262676e684761627269656c6563676e74684741425249454c45ff63646f626a313939382d30322d3236617681bf627467693834303533393030366276706a31313139333035303035626d706c45552f312f32302f31353238626d616d4f52472d31303030333032313562646e01627364026264746a323032312d30322d313862636f6241546269736e424d5347504b2041757374726961626369783075726e3a757663693a30313a41543a313038303738343346393441454530454535303933464243323534424438313350ffff",
    "COSE": "d2844da2044804bde79bdb2ae6600126a0590124a4041a6092dd20061a60903a2001624154390103a101a4617681aa62646e01626d616d4f52472d3130303033303231356276706a313131393330353030356264746a323032312d30322d313862636f624154626369783075726e3a757663693a30313a41543a313038303738343346393441454530454535303933464243323534424438313350626d706c45552f312f32302f313532386269736e424d5347504b20417573747269616273640262746769383430353339303036636e616da463666e74754d5553544552465241553c474f455353494e47455262666e754d7573746572667261752d47c3b6c39f696e67657263676e74684741425249454c4562676e684761627269656c656376657265312e302e3063646f626a313939382d30322d32365840151971b37480c44ffb882793d4d7a073a9367eef3f5ac33a328f17054625e4bfc55cf6f7c038ff08e488090fe20d6cffbb44d7614aa21a79503d7857854e857b",
    "COMPRESSED": "78dabbd4e2bb88c58365eff3d9b7b59e2530aa2d88645459c2229530e9ae029b54c2042b05c624c7104b46e6858c4b12cb1a5725a5e43126e526e6fa07b9eb1a1a1818181b18199a26951564191a1a5a1a1b981a189826a59464190185750d8c740d2d9292f3810624256756189416e559959625675a19185a398658191a5818985b9818bb599a38baba1ab8ba9a1a581abb39391b999a38b958181a0724e516e4b886ea1bea1b19e81b9a1a59246516e739f906bb07782b389616971465262615a7302595a4675a9818981a5b1a189825e725e62e494ecb2b29f50d0d0e710d720b720cb571f7770d0ef6f473770d4a4acb2bf5056a4d2d4a2b4a2cd5753fbcedf0fcccbcf4d4a2e4f4bc920c7747a7204f571fd7a4f4bc0cf7c4a4a2ccd49cd4e4b2d4a254433d033d83e494fca42c434b4b0b90bf8ccc221c44250b3797341cf1ffdda13ef9caf505c52bcdeadedb471db632ea176775537db2ff68ccb7ef072cfe733ce9e0e47fc49bf37fb7cbf544af45529501b615e1ad7eadd500c484830b",
    "BASE45": "NCFOXN%TS3DHMRG2FUPNR9/MPV45NL-AH%TAIOOW%IHOT$E08WAWN0%W0AT4V22F/8X*G3M9JUPY0BX/KR96R/S09T./0LWTKD33236J3TA3M*4VV2 73-E3ND3DAJ-43%*48YIB73A*G3W19UEBY5:PI0EGSP4*2D$43B+2SEB7:I/2DY73CIBC:G 7376BXBJBAJ UNFMJCRN0H3PQN*E33H3OA70M3FMJIJN523S+0B/S7-SN2H N37J3JFTULJ5CB3ZCIATULV:SNS8F-67N%21Q21$48X2+36D-I/2DBAJDAJCNB-43SZ4RZ4E%5B/9OK53:UCT16DEZIE IE9.M CVCT1+9V*QERU1MK93P5 U02Y9.G9/G9F:QQ28R3U6/V.*NT*QM.SY$N-P1S29 34S0BYBRC.UYS1U%O6QKN*Q5-QFRMLNKNM8JI0EUGP$I/XK$M8-L9KDI:ZH2E4UR8 I185JTT3QFWDHK1QV+/UU-OJ1Q 7SP:8M1NWQTP3D/OADSM8BDHBN +0O7WNV7HJS%6G8WJP6GDZPXU8GY8U$I%0N%NST0GX-Q/$OMPG",
    "PREFIX": "HC1:NCFOXN%TS3DHMRG2FUPNR9/MPV45NL-AH%TAIOOW%IHOT$E08WAWN0%W0AT4V22F/8X*G3M9JUPY0BX/KR96R/S09T./0LWTKD33236J3TA3M*4VV2 73-E3ND3DAJ-43%*48YIB73A*G3W19UEBY5:PI0EGSP4*2D$43B+2SEB7:I/2DY73CIBC:G 7376BXBJBAJ UNFMJCRN0H3PQN*E33H3OA70M3FMJIJN523S+0B/S7-SN2H N37J3JFTULJ5CB3ZCIATULV:SNS8F-67N%21Q21$48X2+36D-I/2DBAJDAJCNB-43SZ4RZ4E%5B/9OK53:UCT16DEZIE IE9.M CVCT1+9V*QERU1MK93P5 U02Y9.G9/G9F:QQ28R3U6/V.*NT*QM.SY$N-P1S29 34S0BYBRC.UYS1U%O6QKN*Q5-QFRMLNKNM8JI0EUGP$I/XK$M8-L9KDI:ZH2E4UR8 I185JTT3QFWDHK1QV+/UU-OJ1Q 7SP:8M1NWQTP3D/OADSM8BDHBN +0O7WNV7HJS%6G8WJP6GDZPXU8GY8U$I%0N%NST0GX-Q/$OMPG",
    "TESTCTX": {
        "VERSION": 1,
        "SCHEMA": "1.0.0",
        "CERTIFICATE": "MIIBWTCCAQCgAwIBAgIFAK7oh64wCgYIKoZIzj0EAwIwEDEOMAwGA1UEAwwFRUMtTWUwHhcNMjEwNTAzMTgwMDAwWhcNMjEwNjAyMTgwMDAwWjAQMQ4wDAYDVQQDDAVFQy1NZTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABIQ5ERHXUAPDk3phCru13jtRzJnVcwXYd8jCm0wAez9TFnJhHkxGEW0pvQB7FQJkqcr3H4FDsxaf6Z5i55nQcWOjRzBFMA4GA1UdDwEB/wQEAwIFoDAzBgNVHSUELDAqBgwrBgEEAQCON49lAQEGDCsGAQQBAI43j2UBAgYMKwYBBAEAjjePZQEDMAoGCCqGSM49BAMCA0cAMEQCIA6il0H0Shfie72mZBX+F1PbQXA88HCkAF1HZKjIQW8VAiBiIdQGkNxs3+vpcAwRqrRyXel6y2e/M2Qgr4PWy2Ms5g==",
        "VALIDATIONCLOCK": "2021-05-03T20:00:00+02:00",
        "DESCRIPTION": "VALID: EC 256 key",
        "GATEWAY-ENV":["ACC"]
    },
    "EXPECTEDRESULTS": {
        "EXPECTEDDECODE": true,
        "EXPECTEDVERIFY": true,
        "EXPECTEDUNPREFIX": true,
        "EXPECTEDVALIDJSON": true,
        "EXPECTEDCOMPRESSION": true,
        "EXPECTEDB45DECODE": true
    }
}
```

### Validation Content (TBD)

Javascript validation rules which must be passed during the testing of a 2D Code of the country. Each rule is applied on the decoded JSON Content. The function body is defined as
```
function [name] ([Decoded JSON Object]) {
    return [boolean]
}
```

### Image Content

Contains images of the generated base45 contents(PNG).

### Certificate Content

The public key to validate the data structure. This is defined as base64 encoded datastructure (PEM).

## How to contribute

Contribution and feedback is encouraged and always welcome. For more information about how to contribute, the project structure, as well as additional contribution information, see our [Contribution Guidelines](./CONTRIBUTING.md). By participating in this project, you agree to abide by its [Code of Conduct](./CODE_OF_CONDUCT.md) at all times.


## Licensing

Copyright (C) 2021 T-Systems International GmbH and all other contributors

Licensed under the **Apache License, Version 2.0** (the "License"); you may not use this file except in compliance with the License.

You may obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the [LICENSE](./LICENSE) for the specific
language governing permissions and limitations under the License.
