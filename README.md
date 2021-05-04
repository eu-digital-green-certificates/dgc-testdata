# DGC Test Data Repository for Test Automation

To automate the generation and validation tests of COSE/CBOR Codes and it's base45/2D Code representations, a lot of data has to be collected to ensure the variance of the tests. This respository was established to collect a lot of different test data and related test cases of different member states in a standardized manner. Each member state can generate a folder in this section. 

## 2D Code

### Test Procedure

The test procedure has the following steps: 

1. Load RAW Data File X
2. Apply all test and validation rules to File X (from all countries). 
3. If one rule fails, the RAW Data File X is highlighted with the related Validation Rule/TestName Fail Status. 

**Note**: If some of the "EXPTECEDRESULT" values are not present, the steps in the tests run can be skipped. The related data can be removed then as well. E.g. if just a "Expireing" test is constructed, the "EXPECTEDEXPIRED" value can be set together with an "COSE" and "VALIDATIONCLOCK" raw object. All other fields are then not necessary.


The inline test procedure contains the steps: 

#### Code Generation

| Test Number | Test| Mandatory Fields|Mandatory Test Context Fields| Variable|
|------------ |--|-----------------|------------|-----|
|1            | Load RAW File and load JSON Object, validate against the referenced JSON schema in the test context(SCHEMA field). |JSON| SCHEMA| EXPECTEDVALIDOBJECT|
|2            |Create CBOR from JSON Object. Validate against the CBOR content in the RAW File. |JSON, CBOR||EXPECTEDENCODE|

**NOTE**: DESCRIPTION, VERSION are for all tests mandatory.

#### Code Validation

| Test Number | Test| Mandatory Fields|Mandatory Test Context Fields| Variable|
|------------ |--|-----------------|------------|-----|
| 1           | Load the picture and extract the prefixed BASE45content.  |PREFIX , 2DCode |      |EXPECTEDPICTUREDECODE|
| 2|Load Prefix Object from RAW Content and remove the prefix. Validate against the BASE45 raw content. |PREFIX, BASE45||EXPECTEDUNPREFIX|
| 3|Decode the BASE45 RAW Content and validate the COSE content against the RAW content. |BASE45, COSE|| EXPECTEDB45DECODE|
|4|Check the EXP Field for expiring against the **VALIDATIONCLOCK** time. |COSE| VALIDATIONCLOCK|EXPTECTEDEXPIRED|
|5|Verify the signature of the COSE Object against the JWK Public Key. |COSE| JWK|EXPECTEDVERIFY|
|6|Extract the CBOR content and validate the CBOR content against the RAW CBOR content field. |COSE,CBOR||EXPECTEDDECODE|
|7|Transform CBOR into JSON and validate against the RAW JSON content. |CBOR,JSON||EXPECTEDVALIDJSON|
|8|Validate the extracted JSON against the schema defined in the test context.  |CBOR,JSON|SCHEMA|EXPECTEDSCHEMAVALIDATION|

**NOTE**: DESCRIPTION, VERSION are for all tests mandatory.

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
   "JSON":**JSON OBJECT**, 
   "CBOR":**CBOR (hex encoded)**, 
   "COSE":**COSE (hex encoded)**,  
   "BASE45": **BASE45 Encoded COMP**, 
   "PREFIX": **BASE45 Encoded Compression with Prefix HC(x):**,  
   "2DCODE":**BASE64 Encoded PNG**,
   "TESTCTX":{
               "VERSION":**integer**,
               "SCHEMA":**string (USED SCHEMA)**, (semver) 
               "JWK":**JWK Object** ,
               "VALIDATIONCLOCK":**Timestamp**, (https://docs.jsonata.org/date-time-functions ISO8601)
               "DESCRIPTION":**string**
             },
 "EXPECTEDRESULTS": {
            "EXPECTEDVALIDOBJECT":**boolean**,
            "EXPECTEDSCHEMAVALIDATION":**boolean**,
            "EXPECTEDENCODE":**boolean**,
            "EXPECTEDDECODE":**boolean**,
            "EXPECTEDVERIFY":**boolean**,
            "EXPECTEDUNPREFIX":**boolean**,
            "EXPECTEDVALIDJSON":**boolean**,
            "EXPECTEDB45DECODE":**boolean**,
            "EXPECTEDPICTUREDECODE":**boolean**,
            "EXPTECTEDEXPIRED":**boolean**,
           }
}
 ```     
Example: 
```
{
"JSON":{ "sub": { "gn": "Gabriele", "fn": "Musterfrau", "id": [ { "t": "PPN", "i": "12345ABC-321" } ], "dob": "1998-02-26", "gen": "female" }, "vac": [ { "dis": "840539006", "vap": "1119305005", "mep": "EU\/1\/20\/1528", "aut": "ORG-100030215", "seq": 1, "tot": 2, "dat": "2021-02-18", "cou": "AT", "lot": "C22-862FF-001", "adm": "Vaccination centre Vienna 23" }, { "dis": "840539006", "vap": "1119305005", "mep": "EU\/1\/20\/1528", "aut": "ORG-100030215", "seq": 2, "tot": 2, "dat": "2021-03-12", "cou": "AT", "lot": "C22-H62FF-010", "adm": "Vaccination centre Vienna 23" } ], "cert": { "is": "Ministry of Health, Austria", "id": "01AT42196560275230427402470256520250042", "vf": "2021-04-04", "vu": "2021-10-04", "co": "AT", "vr": "v1.0" } },
"CBOR":"a4041a625eef58061a607dbbd801624154390103a101590207bf63737562bf62676e684761627269656c6562666e6a4d75737465726672617563646f626a313939382d30322d32366367656e6666656d616c656269649fbf61746350504e61696c31323334354142432d333231ffffff637661639fbf6364697369383430353339303036637661706a31313139333035303035636d65706c45552f312f32302f31353238636175746d4f52472d313030303330323135637365710163746f7402636c6f746d4332322d38363246462d303031636461746a323032312d30322d31386361646d781c56616363696e6174696f6e2063656e747265205669656e6e6120323363636f75624154ffbf6364697369383430353339303036637661706a31313139333035303035636d65706c45552f312f32302f31353238636175746d4f52472d313030303330323135637365710263746f7402636c6f746d4332322d48363246462d303130636461746a323032312d30332d31326361646d781c56616363696e6174696f6e2063656e747265205669656e6e6120323363636f75624154ffff6463657274bf626973781b4d696e6973747279206f66204865616c74682c204175737472696162696478273031415434323139363536303237353233303432373430323437303235363532303235303034326276666a323032312d30342d30346276756a323032312d31302d303462636f6241546276726476312e30ffff",
"COSE":"d2844da204489a024e6b59bf42ce0126a0590220a4041a625eef58061a607dbbd801624154390103a101590207bf63737562bf62676e684761627269656c6562666e6a4d75737465726672617563646f626a313939382d30322d32366367656e6666656d616c656269649fbf61746350504e61696c31323334354142432d333231ffffff637661639fbf6364697369383430353339303036637661706a31313139333035303035636d65706c45552f312f32302f31353238636175746d4f52472d313030303330323135637365710163746f7402636c6f746d4332322d38363246462d303031636461746a323032312d30322d31386361646d781c56616363696e6174696f6e2063656e747265205669656e6e6120323363636f75624154ffbf6364697369383430353339303036637661706a31313139333035303035636d65706c45552f312f32302f31353238636175746d4f52472d313030303330323135637365710263746f7402636c6f746d4332322d48363246462d303130636461746a323032312d30332d31326361646d781c56616363696e6174696f6e2063656e747265205669656e6e6120323363636f75624154ffff6463657274bf626973781b4d696e6973747279206f66204865616c74682c204175737472696162696478273031415434323139363536303237353233303432373430323437303235363532303235303034326276666a323032312d30342d30346276756a323032312d31302d303462636f6241546276726476312e30ffff5840cea198d7da5cb609f9b1d0622d3d2824d5a05b0a8cbd0f112ec8be8860be3944ab9f0a4614521328db093570bd64bc2c1d88decdd597578a329b2aa96fbfe906",
"BASE45":"NCFI.L3B6AP2YQ2QIN4U8X*8OVL9EM%9DVYD41QG.JFWRXFUB.NEPELVG5PE:NIEORLXCXXN*QEM7V5+G+W8CQFJRHQ O+ZLPUDBOR52PBH81T20/L./L6A1*HQ6I8//PZ-VBGW9ES-BF81VN%KEYKT6GY.J++TF4Q9:M$7R4FI12GQBP8JTIUTJ17%P9/5O87JYWDCURIVKX59B4K0.MC*FOMUFMPA*SH%QF%C/:ISDJKR93E6:52HAMH9GALFRY9WCCCTFVGTR76+FJ$H14YU ZE:F7Z/LH+P+$1MMK*$OOGHX 5J-IFLJI-Q170GP672F/B4NH0BBG44K*5F8WBJ9IJI8.8AO91KPT51RWC7%20UI0FCLB1T9PI/HM9SHA LFVM%0F+UOLTO 24CAC QGRZEY.87NE5WRX:NWWGIB24H52Q5RM4:69ZFBX45K 2$J8RFJG0CS:2UVUJWA4M89E0H6AM-696G:D5784W+J4+I$YJ1IL/*K$JND:O10RD$L$BRS$L6NV:OK$E744PM740V4VJH6BA+CM0JQT:2B+5 MBTXK: 6A*4NSHU62X+8I%9IC88ERX87BT8-XBB24G 0:F3RMCRTQN9VO1A00EB-3XQV6L05:5Y3KYCSIE6DCE7JR7NTCWN/VL3AWG8JJPU%MPGL2*4CL9DO:4BN7U0DK R*0W 8R0JSSI1DVS3%VI06NIR05",
"PREFIX":"HC1:NCFI.L3B6AP2YQ2QIN4U8X*8OVL9EM%9DVYD41QG.JFWRXFUB.NEPELVG5PE:NIEORLXCXXN*QEM7V5+G+W8CQFJRHQ O+ZLPUDBOR52PBH81T20/L./L6A1*HQ6I8//PZ-VBGW9ES-BF81VN%KEYKT6GY.J++TF4Q9:M$7R4FI12GQBP8JTIUTJ17%P9/5O87JYWDCURIVKX59B4K0.MC*FOMUFMPA*SH%QF%C/:ISDJKR93E6:52HAMH9GALFRY9WCCCTFVGTR76+FJ$H14YU ZE:F7Z/LH+P+$1MMK*$OOGHX 5J-IFLJI-Q170GP672F/B4NH0BBG44K*5F8WBJ9IJI8.8AO91KPT51RWC7%20UI0FCLB1T9PI/HM9SHA LFVM%0F+UOLTO 24CAC QGRZEY.87NE5WRX:NWWGIB24H52Q5RM4:69ZFBX45K 2$J8RFJG0CS:2UVUJWA4M89E0H6AM-696G:D5784W+J4+I$YJ1IL/*K$JND:O10RD$L$BRS$L6NV:OK$E744PM740V4VJH6BA+CM0JQT:2B+5 MBTXK: 6A*4NSHU62X+8I%9IC88ERX87BT8-XBB24G 0:F3RMCRTQN9VO1A00EB-3XQV6L05:5Y3KYCSIE6DCE7JR7NTCWN/VL3AWG8JJPU%MPGL2*4CL9DO:4BN7U0DK R*0W 8R0JSSI1DVS3%VI06NIR05",
"TESTCTX":{
         "VERSION":1,
         "SCHEMA":"1.0.0",
         "JWK":{"x5c":"MIIDQjCCAiqgAwIBAgIGATz/FuLiMA0GCSqGSIb3DQEBBQUAMGIxCzAJB
                gNVBAYTAlVTMQswCQYDVQQIEwJDTzEPMA0GA1UEBxMGRGVudmVyMRwwGgYD
                VQQKExNQaW5nIElkZW50aXR5IENvcnAuMRcwFQYDVQQDEw5CcmlhbiBDYW1
                wYmVsbDAeFw0xMzAyMjEyMzI5MTVaFw0xODA4MTQyMjI5MTVaMGIxCzAJBg
                NVBAYTAlVTMQswCQYDVQQIEwJDTzEPMA0GA1UEBxMGRGVudmVyMRwwGgYDV
                QQKExNQaW5nIElkZW50aXR5IENvcnAuMRcwFQYDVQQDEw5CcmlhbiBDYW1w
                YmVsbDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAL64zn8/QnH
                YMeZ0LncoXaEde1fiLm1jHjmQsF/449IYALM9if6amFtPDy2yvz3YlRij66
                s5gyLCyO7ANuVRJx1NbgizcAblIgjtdf/u3WG7K+IiZhtELto/A7Fck9Ws6
                SQvzRvOE8uSirYbgmj6He4iO8NCyvaK0jIQRMMGQwsU1quGmFgHIXPLfnpn
                fajr1rVTAwtgV5LEZ4Iel+W1GC8ugMhyr4/p1MtcIM42EA8BzE6ZQqC7VPq
                PvEjZ2dbZkaBhPbiZAS3YeYBRDWm1p1OZtWamT3cEvqqPpnjL1XyW+oyVVk
                aZdklLQp2Btgt9qr21m42f4wTw+Xrp6rCKNb0CAwEAATANBgkqhkiG9w0BA
                QUFAAOCAQEAh8zGlfSlcI0o3rYDPBB07aXNswb4ECNIKG0CETTUxmXl9KUL
                +9gGlqCz5iWLOgWsnrcKcY0vXPG9J1r9AqBNTqNgHq2G03X09266X5CpOe1
                zFo+Owb1zxtp3PehFdfQJ610CDLEaS9V9Rqp17hCyybEpOGVwe8fnk+fbEL
                2Bo3UPGrpsHzUoaGpDftmWssZkhpBJKVMJyf/RuP2SmmaIzmnw9JiSlYhzo
                4tpzd5rFXhjRbg4zW9C+2qok+2+qDM1iJ684gPHMIY8aLWrdgQTxkumGmTq
                gawR+N5MDtdPTEQ0XfIBc2cJEUyMTY5MPvACWpkA6SdS4xSvdXK3IVfOWA==", 
                
         
           "VALIDATIONCLOCK":"2017-05-15T15:12:59.152Z",
           "DESCRIPTION":"Verify Fail Test.",
          },
 "EXPECTEDRESULTS":{
                 "EXPECTEDDECODE":true,
                 "EXPECTEDVERIFY":false,
                 "EXPECTEDUNPREFIX":true,
                 "EXPTECTEDEXPIRED":true,
                 "EXPECTEDSCHEMAVALIDATION":true,
                 "EXPECTEDVALIDOBJECT":true

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

### JWK Content

The key pair to validate the data structure. This is defined as x5c datastructure which contains the public key.
