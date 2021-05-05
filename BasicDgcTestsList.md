
This List contains common Test Cases which should be passed by any DGC Validators. 


|ID|Component|Business Description|Validity|Testdataset| Known Implementations|
|--|--|--------------------|--------------------|--|--|
|Q2|QR|Other QR encoding than alphanumeric used|INVALID|
|H1|Context|Context does not match schema (e.g. HL0:)|INVALID|
|H2|Context|Context value not supported (e.g. HL1:)|INVALID|
|H3|Context|Context value missing (only BASE45 encoding)|INVALID|
|B1|BASE45|BASE45 invalid (wrong encoding characters)|INVALID|
|Z1|ZLIB|Compression broken|INVALID|
|Z2|ZLIB|Not compressed|INVALID|
|CO1|COSE/CWT|Algorithm PS256 with RSA 2048|VALID|
|CO2|COSE/CWT|Algorithm PS256 with RSA 3072|VALID|
|CO3|COSE/CWT|Algorithm PS256 with ES256|VALID|
|CO4|COSE/CWT|Algorithm not supported (other then ES256/PS256)|INVALID|
|CO5|COSE/CWT|Signature cryptographically invalid|INVALID|
|CO6|COSE/CWT|OID for Test present, but DGC for vacc|INVALID|
|CO7|COSE/CWT|OID for Test present, but DGC for recovery|INVALID|
|CO8|COSE/CWT|OID for Vacc present, but DGC for test|INVALID|
|CO9|COSE/CWT|OID for Vacc present, but DGC for recovery|INVALID|
|CO10|COSE/CWT|OID for Recovery present, but DGC for vacc|INVALID|
|CO11|COSE/CWT|OID for Recovery present, but DGC for test|INVALID|
|CO12|COSE/CWT|OID for Test present, DGC is test|VALID|
|CO13|COSE/CWT|OID for Vacc present, DGC is vacc|VALID|
|CO14|COSE/CWT|OID for Recovery present, DGC is recovery|VALID|
|CO15|COSE/CWT|no OID present, DGC is recovery, test or vacc|VALID|
|CO16|COSE/CWT|validation clock before "ISSUED AT"|INVALID|
|CO17|COSE/CWT|validation clock after "expired"|INVALID|
|CO18|COSE/CWT|KID in protected header **correct**, KID in unprotected header **not present**|VALID|
|CO19|COSE/CWT|KID in protected header **not present**, KID in unprotected header **correct**|VALID|
|CO20|COSE/CWT|KID in protected header **correct**, KID in unprotected header **correct**|VALID|
|CO21|COSE/CWT|KID in protected header **correct**, KID in unprotected header **not correct**|VALID|
|CO22|COSE/CWT|KID in protected header **not correct**, KID in unprotected header **correct**|INVALID|
|CO23|COSE/CWT|KID in protected header **not present**, KID in unprotected header **not correct**|INVALID|
|CB01|CBOR|wrong CBOR structure|INVALID|
|CB02|CBOR|wrong CWT structure|INVALID|
|DGC1|DGC|DGC does not adhere to schema|INVALID|
|DGC2|DGC|DGC adheres to schema but contains multiple certificates|INVALID|
|DGC3|DGC|correct test1 DGC|VALID|
|DGC4|DGC|correct test2 DGC|VALID|
|DGC5|DGC|correct recovery DGC|VALID|
|DGC6|DGC|correct vacc DGC|VALID|
