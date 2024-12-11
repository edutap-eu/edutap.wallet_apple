import os
from pathlib import Path
from typing import Optional, Union
import cryptography
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization.pkcs7 import (
    PKCS7SignatureBuilder, PKCS7Options
)

class VerificationError(Exception):
    """
    backend-independent 
    """

def sign_manifest(
    manifest: str,
    certificate_path: Union[str, Path],
    private_key_path: Union[str, Path],
    wwdr_certificate_path: Union[str, Path],
    password: Optional[bytes]=None,
) -> bytes:
    """
    :param manifest: contains the manifest content as json string
    :param certificate: path to certificate
    :param key: path to private key
    :wwdr_certificate: path to wwdr_certificate
    :return: signature as bytes
    """

    # PKCS7: see https://www.youtube.com/watch?v=3YJ0by1r3qE
    with open(certificate_path, "rb") as fh:
        certificate_data = fh.read()
    with open(private_key_path, "rb") as fh:
        private_key_data = fh.read()
    with open(wwdr_certificate_path, "rb") as fh:
        wwdr_certificate_data = fh.read()

    certificate = load_pem_x509_certificate(certificate_data, default_backend())
    private_key = load_pem_private_key(
        private_key_data, password=password, backend=default_backend()
    )
    # if not isinstance(private_key, (RSAPrivateKey, EllipticCurvePrivateKey)):
    #     raise TypeError("Private key must be an RSAPrivateKey or EllipticCurvePrivateKey")
    wwdr_certificate = load_pem_x509_certificate(
        wwdr_certificate_data, default_backend()
    )

    signature_builder = (
        PKCS7SignatureBuilder()
        .set_data(manifest.encode("utf-8"))
        .add_signer(certificate, private_key, hashes.SHA256())
        .add_certificate(wwdr_certificate)
    )

    pkcs7_signature = signature_builder.sign(Encoding.DER, [])
    return pkcs7_signature


def create_signature(
    manifest: str,
    certificate_path: Union[str, Path],
    private_key_path: Union[str, Path],
    wwdr_certificate_path: Union[str, Path],
    password: Optional[bytes] = None,
) -> bytes:
    """
    Creates the signature for the pass file.
    """

    # check for cert file existence
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Key file {private_key_path} not found")
    if not os.path.exists(certificate_path):
        raise FileNotFoundError(f"Certificate file {certificate_path} not found")
    if not os.path.exists(wwdr_certificate_path):
        raise FileNotFoundError(
            f"WWDR Certificate file {wwdr_certificate_path} not found"
        )

    pk7 = sign_manifest(
        manifest,
        certificate_path,
        private_key_path,
        wwdr_certificate_path,
        password,
    )

    return pk7


def verify_manifest(manifest: str, signature: bytes):
    """
    Verifies the manifest against the signature.
    Currently no check against the cert supported, only the
    manifest is verified against the signature to check for manipulation
    in the manifest
    :param: manifest as a json string
    :param: signature as PKCS#7 signature

    Attention: this is work in progress since we need to add a feature to
    the `cryptography` library to support the verification of the PKCS#7 signatures
    therefore we filed a [Pull request](https://github.com/pyca/cryptography/pull/12116)
    """
    from cryptography.hazmat.bindings._rust import test_support # this is preliminary hence the local import

    # if cert_pem:
    #     with  open(cert_pem, "rb") as fh:
    #         cert = load_pem_x509_certificate(fh.read(), default_backend())
    # else:
    #     cert = None

    try:
        test_support.pkcs7_verify(
            Encoding.DER,
            signature,
            manifest.encode("utf-8"),
            [], #
            [PKCS7Options.NoVerify],
        )
    except cryptography.exceptions.InternalError as ex:
        raise VerificationError(ex)