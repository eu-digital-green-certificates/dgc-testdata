# Germany

---

## Test files

### 1 - Tina Testerin

[1.json](2DCode/raw/1.json) - Basic DGC with one vaccination entry. Signed with the first DSC.

All tests should be successful.

![1](2DCode/png/1.png)

### 2 - Erika Musterfrau

[2.json](2DCode/raw/2.json) - Basic DGC with one vaccination entry. Signed with a second DSC.

All tests should be successful.

![2](2DCode/png/2.png)

### 3 - Max Mustermann

[3.json](2DCode/raw/3.json) - Basic DGC with one vaccination entry. Signed with a third key, not the DSC indicated.

Signature validation should fail.

![3](2DCode/png/3.png)
