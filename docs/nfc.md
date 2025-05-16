# NFC Support

## Generating an ECC Key Pair

To be able to tap with a pass using a specific reader, an ECC key pair must be generated. The public key belongs in the NFC record of the pass, while the private key must be stored on the reader. This, of course, depends on the specific manufacturer.

⚠️ **Note:**: The private key used here has nothing to do with the private key used to generate the Apple Pass certificate.

The private key can be generated with:

```bash
openssl ecparam -name prime256v1 -genkey -out private.pem
```

From this, we extract the public key:

```bash
openssl ec -in private.pem -pubout -conv_form compressed -out apple_public.pem
```

In the corresponding sample project, this key must then be saved in the directory
`data/certs/nfc/{pass_type_id}/apple_public.pem`.

During the pass creation this public key lands in the pass.json in the pkpass in
the `nfc` section in the `encryptionPublicKey` field like so:

```json 
    "nfc": {
        "message": "Hello NFC pass.demo.lmu.de 56c972a7-c3ca-4415-885c-42496ee3e58",
        "encryptionPublicKey": "MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgAC5l2N1kcSduIFf/DYrmcqL45V8ExdtYQK0LjUs8wiBNA=",
        "requiresAuthentication": false
    },
```

So in the example of pass.demo.lmu.de, the file path would be:
`data/certs/nfc/pass.demo.lmu.de/apple_public.pem`

The private key `private.pem` must then be stored on the reader, see the reader documentation how to do that.

When the user taps the pass on the reader this ECC pair will be used to decrypt the answer from the 
phone that holds the pass to the reader.

### dotorigin VTAP

For dotorigin, the PEM-encoded key must be copied to the root directory with the filename `private{Slot Number}.pem`, where the slot numbers range from 1 to 6.

The device must then be restarted. After that, the file will no longer be visible.

#### Example

for example if you do this for the pass type id `pass.demo.lmu.de`, you copy the key under the name `private1.pem` to the device FS.

Further you have to specify the pass in the `config.txt`:

```txt
...
VAS1MerchantID=pass.demo.lmu.de
VAS1KeySlot=1
...
```

#### Further reading
- [Dotorigin Configuration Guide](https://www.vtapnfc.com/downloads/VTAP_Configuration_Guide.pdf)
- [configuring and key delivery for dotorigin VTAP reader](https://www.vtapnfc.com/downloads/VTAP_AN_ECC_key_pairs.pdf)
- [vanilla config text](https://www.vtapnfc.com/downloads/config.txt)
 in case you brick the reader, you can reset the config.txt
