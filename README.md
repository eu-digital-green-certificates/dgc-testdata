# DGC Test Data Repository for Test Automation

To automate the generation and validation tests of COSE/CBOR Codes and it's base45/2D Code representations, a lot of data has to be collected to ensure the variance of the tests. This respository was established to collect a lot of different test data and related test cases of different member states in a standardized manner. Each member state can generate a folder in this section. 

## 2D Code

### Test Procedure

The test procedure has the following steps: 

1. Load RAW Data File X
2. Apply all test and validation rules to File X (from all countries). 
3. If one rule fails, the RAW Data File X is highlighted with the related Validation Rule/TestName Fail Status. 

**Note**: If some of the "EXPTECEDRESULT" values are not present, the steps in the tests run can be skipped. The related data can be removed then as well. E.g. if just a "Expireing" test is constructed, the "EXPECTEDEXPIRATIONCHECK" value can be set together with an "COSE" and "VALIDATIONCLOCK" raw object. All other fields are then not necessary.


The inline test procedure contains the steps: 

#### Code Generation

| Test Number | Test| Mandatory Fields|Mandatory Test Context Fields| Variable|
| :--- | :--- | :--- | :--- | :--- |
|1            | Load RAW File and load JSON Object, validate against the referenced JSON schema in the test context(SCHEMA field). |JSON| SCHEMA| EXPECTEDVALIDOBJECT|
|2            |Create CBOR from JSON Object. Validate against the CBOR content in the RAW File. See note 2 below. |JSON, CBOR||EXPECTEDENCODE|

**NOTE**: DESCRIPTION, VERSION are mandatory for all tests.

**NOTE 2**: CBOR objects that are maps (i.e., the Digital Green Certificate), have an undefined order. This means that the actual encodings between two objects containing the same elements may differ since the ordering may be different. Therefore the validation can not be as simple as comparing two byte arrays against each other. The best method is to decode both elements that are to be compared with the same decoder, encode both objects with the same encoder, and then compare.

#### Code Validation

| Test Number | Test| Mandatory Fields|Mandatory Test Context Fields| Variable|
| :--- | :--- | :--- | :--- | :--- |
| 1           | Load the picture and extract the prefixed BASE45content.  |PREFIX , 2DCode |      |EXPECTEDPICTUREDECODE|
| 2|Load Prefix Object from RAW Content and remove the prefix. Validate against the BASE45 raw content. |PREFIX, BASE45||EXPECTEDUNPREFIX|
| 3|Decode the BASE45 RAW Content and validate the COSE content against the RAW content. |BASE45, COSE|| EXPECTEDB45DECODE|
|4|Check the EXP Field for expiring against the **VALIDATIONCLOCK** time. |COSE| VALIDATIONCLOCK|EXPECTEDEXPIRATIONCHECK|
|5|Verify the signature of the COSE Object against the JWK Public Key. |COSE| JWK|EXPECTEDVERIFY|
|6|Extract the CBOR content and validate the CBOR content against the RAW CBOR content field. See note 2 below. |COSE,CBOR||EXPECTEDDECODE|
|7|Transform CBOR into JSON and validate against the RAW JSON content. See note 3 below. |CBOR,JSON||EXPECTEDVALIDJSON|
|8|Validate the extracted JSON against the schema defined in the test context.  |CBOR,JSON|SCHEMA|EXPECTEDSCHEMAVALIDATION|

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

The  JSON Content under RAW is defined as: 
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
       "DESCRIPTION": **string**
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
    "CBOR": "a4041a6092dd20061a60903a2001624154390103a101a4617681aa62646e01626d616d4f52472d3130303033303231356276706a313131393330353030356264746a323032312d30322d313862636f624154626369783075726e3a757663693a30313a41543a313038303738343346393441454530454535303933464243323534424438313350626d706c45552f312f32302f313532386269736e424d5347504b20417573747269616273640262746769383430353339303036636e616da463666e74754d5553544552465241553c474f455353494e47455262666e754d7573746572667261752d47c3b6c39f696e67657263676e74684741425249454c4562676e684761627269656c656376657265312e302e3063646f626a313939382d30322d3236",
    "COSE": "d2844da20448c27cf6f2194e44450126a0590124a4041a6092dd20061a60903a2001624154390103a101a4617681aa62646e01626d616d4f52472d3130303033303231356276706a313131393330353030356264746a323032312d30322d313862636f624154626369783075726e3a757663693a30313a41543a313038303738343346393441454530454535303933464243323534424438313350626d706c45552f312f32302f313532386269736e424d5347504b20417573747269616273640262746769383430353339303036636e616da463666e74754d5553544552465241553c474f455353494e47455262666e754d7573746572667261752d47c3b6c39f696e67657263676e74684741425249454c4562676e684761627269656c656376657265312e302e3063646f626a313939382d30322d323658407376bf4d450f2b9796edc5c8599f040c43c0a0ca944e923260af639adf9039b11b9797e8ff0ce9230b9a16d4aaeb2de5a7aad8bb9b65945b5764a8e9a685181a",
    "COMPRESSED": "78da017a0185fed2844da20448c27cf6f2194e44450126a0590124a4041a6092dd20061a60903a2001624154390103a101a4617681aa62646e01626d616d4f52472d3130303033303231356276706a313131393330353030356264746a323032312d30322d313862636f624154626369783075726e3a757663693a30313a41543a313038303738343346393441454530454535303933464243323534424438313350626d706c45552f312f32302f313532386269736e424d5347504b20417573747269616273640262746769383430353339303036636e616da463666e74754d5553544552465241553c474f455353494e47455262666e754d7573746572667261752d47c3b6c39f696e67657263676e74684741425249454c4562676e684761627269656c656376657265312e302e3063646f626a313939382d30322d323658407376bf4d450f2b9796edc5c8599f040c43c0a0ca944e923260af639adf9039b11b9797e8ff0ce9230b9a16d4aaeb2de5a7aad8bb9b65945b5764a8e9a685181a24398437",
    "BASE45": "NCFI80T80T9WTWGVLK-89+ZFCRUB+9PW8X*4FBBKS4FN0H9C/.RWY0F9CUF7*70TB8D97TK0F90KECTHGXJC +D.JCBECB1A-:8$966469L6OF6VX6Z/E5JD%96IA7B46646VX6LVC6JD846Y968464W5Y57UPC/IC2UAOPCX8F6%E3.DA%EOPC1G72A6TB82G7E46D46X47VL6JA7EB8RX83Y8QW6IA7V*8CM8UW6:G8U47-L6.JCP9EJY8L/5M/5546.96VF6%JCUQE8H8YNAZ6AM347%EKWEMED3KC.SC4KCD3DX47B46IL6646I*6..DX%DLPCG/DE$EIZAITA2IA.HA+YAU09HY8 NAE+9GY8ZJCH/DTZ9 QE5$C .CJECQW5HXO*WOZED93DXKEI3DAWEG09DH8$B9+S9 JC4/D3192KCQEDTVD$PC5$CUZCY$5Y$5JPCT3E5JDOA7Q478465W57*6T68O0FQY9D-1G7JT2UYEPS4KYO1$FOKRP:-9QG6Y7M2QJLAIOHMH7JMKTKS1GJ4QLJ$*Q+WTL1T-QLCWN*$CSOBSWC9OT7$GWD39C7A1",
    "PREFIX": "HC1:NCFI80T80T9WTWGVLK-89+ZFCRUB+9PW8X*4FBBKS4FN0H9C/.RWY0F9CUF7*70TB8D97TK0F90KECTHGXJC +D.JCBECB1A-:8$966469L6OF6VX6Z/E5JD%96IA7B46646VX6LVC6JD846Y968464W5Y57UPC/IC2UAOPCX8F6%E3.DA%EOPC1G72A6TB82G7E46D46X47VL6JA7EB8RX83Y8QW6IA7V*8CM8UW6:G8U47-L6.JCP9EJY8L/5M/5546.96VF6%JCUQE8H8YNAZ6AM347%EKWEMED3KC.SC4KCD3DX47B46IL6646I*6..DX%DLPCG/DE$EIZAITA2IA.HA+YAU09HY8 NAE+9GY8ZJCH/DTZ9 QE5$C .CJECQW5HXO*WOZED93DXKEI3DAWEG09DH8$B9+S9 JC4/D3192KCQEDTVD$PC5$CUZCY$5Y$5JPCT3E5JDOA7Q478465W57*6T68O0FQY9D-1G7JT2UYEPS4KYO1$FOKRP:-9QG6Y7M2QJLAIOHMH7JMKTKS1GJ4QLJ$*Q+WTL1T-QLCWN*$CSOBSWC9OT7$GWD39C7A1",
    "TESTCTX": {
        "VERSION": 1,
        "SCHEMA": "1.0.0",
        "CERTIFICATE": "MIIBWjCCAQCgAwIBAgIFAM35dB0wCgYIKoZIzj0EAwIwEDEOMAwGA1UEAwwFRUMtTWUwHhcNMjEwNTAzMTgwMDAwWhcNMjEwNjAyMTgwMDAwWjAQMQ4wDAYDVQQDDAVFQy1NZTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABB5HI4yjHBVgyEb6iDQYP9xtP8VBoQ6JVjEWGcDEYQlB8LDxYdwrUpwNTT3BRJpRW+84qgwLP+7LQ3Y9kZSwqQGjRzBFMA4GA1UdDwEB/wQEAwIFoDAzBgNVHSUELDAqBgwrBgEEAQCON49lAQEGDCsGAQQBAI43j2UBAgYMKwYBBAEAjjePZQEDMAoGCCqGSM49BAMCA0gAMEUCIQCvm7SBTzlRU9XjW02JEfksU26ll+L12ZSvHg5kQvOJVQIge6//uvQejatCQKvPMdMfQfMdPy1pn3FqAzWffXeZ+ow=",
        "VALIDATIONCLOCK": "2021-05-03T20:00:00+02:00",
        "DESCRIPTION": "VALID: EC 256 key"
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
