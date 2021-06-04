# Verifier Validity Checks

This List contains common Test Cases which should be passed by any DGC Validators. 


| ID   | Component | Business Description                                                               | Validity | Testdataset                              | Known Implementations |
|------|-----------|------------------------------------------------------------------------------------|----------|------------------------------------------|-----------------------|
| Q1   | QR        | QR encoding broken                                                                 | INVALID  | [Q1.json](common/2DCode/raw/Q1.json)     |                       |
| Q2   | QR        | Other QR encoding than alphanumeric used                                           | INVALID  | missing                                  |                       |
| H1   | Context   | Context does not match schema (e.g. HL0:)                                          | INVALID  | [H1.json](common/2DCode/raw/H1.json)     |                       |
| H2   | Context   | Context value not supported (e.g. HL1:)                                            | INVALID  | [H2.json](common/2DCode/raw/H2.json)     |                       |
| H3   | Context   | Context value missing (only BASE45 encoding)                                       | INVALID  | [H3.json](common/2DCode/raw/H3.json)     |                       |
| B1   | BASE45    | BASE45 invalid (wrong encoding characters)                                         | INVALID  | [B1.json](common/2DCode/raw/B1.json)     |                       |
| Z1   | ZLIB      | Compression broken                                                                 | INVALID  | [Z1.json](common/2DCode/raw/Z1.json)     |                       |
| Z2   | ZLIB      | Not compressed                                                                     | INVALID  | [Z2.json](common/2DCode/raw/Z2.json)     |                       |
| CO1  | COSE/CWT  | Algorithm PS256 with RSA 2048                                                      | VALID    | [CO1.json](common/2DCode/raw/CO1.json)   |                       |
| CO2  | COSE/CWT  | Algorithm PS256 with RSA 3072                                                      | VALID    | [CO2.json](common/2DCode/raw/CO2.json)   |                       |
| CO3  | COSE/CWT  | Algorithm ES256                                                                    | VALID    | [CO3.json](common/2DCode/raw/CO3.json)   |                       |
| CO4  | COSE/CWT  | Algorithm not supported (other then ES256/PS256)                                   | INVALID  |                                          |                       |
| CO5  | COSE/CWT  | Signature cryptographically invalid                                                | INVALID  | [CO5.json](common/2DCode/raw/CO5.json)   |                       |
| CO6  | COSE/CWT  | OID for Test present, but DGC for vacc                                             | INVALID  | [CO6.json](common/2DCode/raw/CO6.json)   |                       |
| CO7  | COSE/CWT  | OID for Test present, but DGC for recovery                                         | INVALID  | [CO7.json](common/2DCode/raw/CO7.json)   |                       |
| CO8  | COSE/CWT  | OID for Vacc present, but DGC for test                                             | INVALID  | [CO8.json](common/2DCode/raw/CO8.json)   |                       |
| CO9  | COSE/CWT  | OID for Vacc present, but DGC for recovery                                         | INVALID  | [CO9.json](common/2DCode/raw/CO9.json)   |                       |
| CO10 | COSE/CWT  | OID for Recovery present, but DGC for vacc                                         | INVALID  | [CO10.json](common/2DCode/raw/CO10.json) |                       |
| CO11 | COSE/CWT  | OID for Recovery present, but DGC for test                                         | INVALID  | [CO11.json](common/2DCode/raw/CO11.json) |                       |
| CO12 | COSE/CWT  | OID for Test present, DGC is test                                                  | VALID    | [CO12.json](common/2DCode/raw/CO12.json) |                       |
| CO13 | COSE/CWT  | OID for Vacc present, DGC is vacc                                                  | VALID    | [CO13.json](common/2DCode/raw/CO13.json) |                       |
| CO14 | COSE/CWT  | OID for Recovery present, DGC is recovery                                          | VALID    | [CO14.json](common/2DCode/raw/CO14.json) |                       |
| CO15 | COSE/CWT  | no OID present, DGC is recovery, test or vacc                                      | VALID    | [CO15.json](common/2DCode/raw/CO15.json) |                       |
| CO16 | COSE/CWT  | validation clock before "ISSUED AT"                                                | INVALID  | [CO16.json](common/2DCode/raw/CO16.json) |                       |
| CO17 | COSE/CWT  | validation clock after "expired"                                                   | INVALID  | [CO17.json](common/2DCode/raw/CO17.json) |                       |
| CO18 | COSE/CWT  | KID in protected header **correct**, KID in unprotected header **not present**     | VALID    | [CO18.json](common/2DCode/raw/CO18.json) |                       |
| CO19 | COSE/CWT  | KID in protected header **not present**, KID in unprotected header **correct**     | VALID    | [CO19.json](common/2DCode/raw/CO19.json) |                       |
| CO20 | COSE/CWT  | KID in protected header **correct**, KID in unprotected header **correct**         | VALID    | [CO20.json](common/2DCode/raw/CO20.json) |                       |
| CO21 | COSE/CWT  | KID in protected header **correct**, KID in unprotected header **not correct**     | VALID    | [CO21.json](common/2DCode/raw/CO21.json) |                       |
| CO22 | COSE/CWT  | KID in protected header **not correct**, KID in unprotected header **correct**     | INVALID  | [CO22.json](common/2DCode/raw/CO22.json) |                       |
| CO23 | COSE/CWT  | KID in protected header **not present**, KID in unprotected header **not correct** | INVALID  | [CO23.json](common/2DCode/raw/CO23.json) |                       |
| CO24 | COSE/CWT  | A wrong generated ECDSA Signature (longer than 70 bytes) should not lead to an crash                       | INVALID  |  |  
| CO25 | COSE/CWT  | KID is less than 8 byte                       | INVALID  |  |  
| CO26 | COSE/CWT  | KID is greater than 8 byte                      | INVALID  |  |  
| CO27 | COSE/CWT  | Wrong algorithm ID (e.g. RSA with ECDSA signature) MUST lead to invalid.                     | INVALID  |  |  
| CO28 | COSE/CWT  | Message is double tagged. (CWT Tag and COSE Tag)                     | VALID  | [CO28.json](common/2DCode/raw/CO28.json) |  
| CBO1 | CBOR      | wrong CBOR structure                                                               | INVALID  | [CBO1.json](common/2DCode/raw/CBO1.json) |                       |
| CBO2 | CBOR      | wrong CWT structure                                                                | INVALID  | [CBO2.json](common/2DCode/raw/CBO2.json) |                       |
| DGC1 | DGC       | DGC does not adhere to schema                                                      | INVALID  | [DGC1.json](common/2DCode/raw/DGC1.json) |                       |
| DGC2 | DGC       | DGC adheres to schema but contains multiple certificates                           | INVALID  | [DGC2.json](common/2DCode/raw/DGC2.json) |                       |
| DGC3 | DGC       | correct test1 DGC                                                                  | VALID    | [DGC3.json](common/2DCode/raw/DGC3.json) |                       |
| DGC4 | DGC       | correct test2 DGC                                                                  | VALID    | [DGC4.json](common/2DCode/raw/DGC4.json) |                       |
| DGC5 | DGC       | correct recovery DGC                                                               | VALID    | [DGC5.json](common/2DCode/raw/DGC5.json) |                       |
| DGC6 | DGC       | correct vacc DGC                                                                   | VALID    | [DGC6.json](common/2DCode/raw/DGC6.json) |                       |
| DGC7 | DGC       | Correct result for Test Result "260373001" (detected")                             | INVALID  |  | https://github.com/eu-digital-green-certificates/dgca-app-core-ios/blob/main/Sources/Models/TestEntry.swift#L68
|DGC8  | DGC       | The verifier app must show a correct result for future sample timestamps           | INVALID || https://github.com/eu-digital-green-certificates/dgca-app-core-ios/blob/main/Sources/Models/TestEntry.swift#L68


# Issuer Quality Checks

| ID   | Component | Business Description                                        | Testdataset    | Known Implementations |
|------|-----------|-------------------------------------------------------------|--------------|------------------------|
|I-CO1 | COSE/CWT  | The CWT iss field MUST contain an valid ISO 3166-1 alpha-2  |              | |
|I-CO2 | COSE/CWT  | The kid field MUST contain a 8-byte value                       | |
|I-CO3 | COSE/CWT  | Used EC certificates MUST use prime256v1                    | |
|I-CO4 | COSE/CWT  | Issuing Date and Expiration Date MUST be INT Values (Seconds since epoch)                  | |
|I-CO5 | COSE/CWT  | CBOR Object contains no undefined Values                 | |
