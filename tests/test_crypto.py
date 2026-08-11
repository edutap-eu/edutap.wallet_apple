from cryptography.hazmat.primitives.serialization import pkcs7
from edutap.wallet_apple.crypto import create_keys
from edutap.wallet_apple.crypto import sign_pkcs7


def test_sign_pkcs7_detached_does_not_embed_data(signing_material):
    key, cert, wwdr = create_keys(*signing_material)
    data = b'{"hello":"world"}'
    sig = sign_pkcs7(data, key, cert, wwdr, detached=True)
    # detached signature does NOT embed the data
    assert data not in sig
    # it is valid DER PKCS7 that carries the signer cert
    loaded = pkcs7.load_der_pkcs7_certificates(sig)
    assert any(c == cert for c in loaded)


def test_sign_pkcs7_attached_embeds_data(signing_material):
    key, cert, wwdr = create_keys(*signing_material)
    data = b'{"hello":"world"}'
    sig = sign_pkcs7(data, key, cert, wwdr)  # detached defaults to False
    # attached signature embeds the signed data
    assert data in sig
    loaded = pkcs7.load_der_pkcs7_certificates(sig)
    assert any(c == cert for c in loaded)
