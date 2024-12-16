from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7Options
from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7SignatureBuilder
from cryptography.x509 import load_pem_x509_certificate
from pathlib import Path
from typing import Optional
from typing import Union

import cryptography
import os


class VerificationError(Exception):
    """
    backend-independent
    """


def sign_manifest(
    manifest: str,
    private_key: bytes,
    certificate: bytes,
    wwdr_certificate: bytes,
    password: Optional[bytes] = None,
) -> bytes:
    """
    :param manifest: contains the manifest content as json string
    :param certificate: path to certificate
    :param key: path to private key
    :wwdr_certificate: path to wwdr_certificate
    :return: pkcs7 signature as bytes
    """

    # PKCS7: see https://www.youtube.com/watch?v=3YJ0by1r3qE
    signature_builder = (
        PKCS7SignatureBuilder()
        .set_data(manifest.encode("utf-8"))
        .add_signer(certificate, private_key, hashes.SHA256())
        .add_certificate(wwdr_certificate)
    )

    pkcs7_signature = signature_builder.sign(Encoding.DER, [])
    return pkcs7_signature


def load_key_files(
    private_key_path: Union[str, Path],
    certificate_path: Union[str, Path],
    wwdr_certificate_path: Union[str, Path],
    password: Optional[bytes] = None,
) -> tuple[bytes, bytes, bytes]:
    """
    :param private_key_path: path to private key
    :param certificate_path: path to Apple certificate
    :param wwdr_certificate_path: path to Apple WWDR certificate
    :return: tuple of private key, certificate and wwdr_certificate as bytes

    all certs are expected to be in PEM format
    """
    with open(private_key_path, "rb") as fh:
        private_key_data = fh.read()
    with open(certificate_path, "rb") as fh:
        certificate_data = fh.read()
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

    return private_key, certificate, wwdr_certificate


def create_signature(
    manifest: str,
    private_key_path: Union[str, Path],
    certificate_path: Union[str, Path],
    wwdr_certificate_path: Union[str, Path],
    password: Optional[bytes] = None,
) -> bytes:
    """
    :param manifest: contains the manifest content as json string
    :param private_key_path: path to private key
    :param certificate_path: path to Apple certificate
    :param wwdr_certificate_path: path to Apple WWDR certificate
    :return: tuple of private key, certificate and wwdr_certificate as bytes

    all certs are expected to be in PEM format"""

    # check for cert file existence
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Key file {private_key_path} not found")
    if not os.path.exists(certificate_path):
        raise FileNotFoundError(f"Certificate file {certificate_path} not found")
    if not os.path.exists(wwdr_certificate_path):
        raise FileNotFoundError(
            f"WWDR Certificate file {wwdr_certificate_path} not found"
        )

    private_key, certificate, wwdr_certificate = load_key_files(
        private_key_path,
        certificate_path,
        wwdr_certificate_path,
    )

    pk7 = sign_manifest(
        manifest,
        private_key,
        certificate,
        wwdr_certificate,
        password,
    )

    return pk7


def verify_manifest(manifest: str | bytes, signature: bytes):
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
    from cryptography.hazmat.bindings._rust import (
        test_support,  # this is preliminary hence the local import
    )

    # if cert_pem:
    #     with  open(cert_pem, "rb") as fh:
    #         cert = load_pem_x509_certificate(fh.read(), default_backend())
    # else:
    #     cert = None

    if isinstance(manifest, str):
        manifest = manifest.encode("utf-8")

    try:
        test_support.pkcs7_verify(
            Encoding.DER,
            signature,
            manifest,
            [],  #
            [PKCS7Options.NoVerify],
        )
    except cryptography.exceptions.InternalError as ex:
        raise VerificationError(ex)


def supports_verification():
    """
    Checks if the current version of the `cryptography` library supports
    the verification of PKCS#7 signatures

    since support for verification depends on [Pull request](https://github.com/pyca/cryptography/pull/12116)
    this can be checked here
    """
    from cryptography.hazmat.bindings._rust import (
        test_support,  # this is preliminary hence the local import
    )

    return hasattr(PKCS7Options, "NoVerify")
