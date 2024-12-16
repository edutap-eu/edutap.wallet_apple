# pylint: disable=redefined-outer-name
from common import certs, key_files_exist, only_test_if_crypto_supports_verification
from common import create_shell_pass
from common import data
from common import resources
from common import generated_passes_dir, apple_passes_dir
from edutap.wallet_apple import crypto
from edutap.wallet_apple.models import passes
from edutap.wallet_apple.models.passes import Barcode
from edutap.wallet_apple.models.passes import BarcodeFormat
from edutap.wallet_apple.models.passes import EventTicket
from edutap.wallet_apple.models.passes import NFC
from edutap.wallet_apple.models.passes import Pass
from edutap.wallet_apple.models.passes import PkPass
from edutap.wallet_apple.models.passes import StoreCard

import common
import os
import pytest
import uuid



@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_signing():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """

    passfile = create_shell_pass()
    manifest_json = passfile._create_manifest()

    key, cert, wwdr_cert = crypto.load_key_files(
        common.key_file, common.cert_file, common.wwdr_file
    )
    signature = crypto.sign_manifest(
        manifest_json,
        key,
        cert,
        wwdr_cert,
    )

    crypto.verify_manifest(manifest_json, signature)
    tampered_manifest = '{"pass.json": "foobar"}'

    # Verification MUST fail!
    with pytest.raises(crypto.VerificationError):
        crypto.verify_manifest(tampered_manifest, signature)


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_signing1():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """

    passfile = create_shell_pass()
    manifest_json = passfile._create_manifest()

    key, cert, wwdr_cert = crypto.load_key_files(
        common.key_file, common.cert_file, common.wwdr_file
    )
    signature = crypto.sign_manifest(
        manifest_json,
        key,
        cert,
        wwdr_cert,
    )

    crypto.verify_manifest(manifest_json, signature)
    #tamper manifest by changing an attribute
    passfile.pass_object.organizationName = "new organization"
    tampered_manifest = passfile._create_manifest()

    # Verification MUST fail!
    with pytest.raises(crypto.VerificationError):
        crypto.verify_manifest(tampered_manifest, signature)

    passfile = create_shell_pass()
    passfile._add_file("icon.png", open(common.resources / "white_square.png", "rb"))
    passfile._sign(common.key_file, common.cert_file, common.wwdr_file)
    
    zipfile = passfile._as_zip()


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@only_test_if_crypto_supports_verification
@pytest.mark.integration
def test_verification():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """

    passfile = create_shell_pass()
    passfile._add_file("icon.png", open(common.resources / "white_square.png", "rb"))
    passfile._sign(common.key_file, common.cert_file, common.wwdr_file)
    manifest = passfile._create_manifest()
    signature = passfile.files["signature"]
    crypto.verify_manifest(manifest, signature)
    passfile.verify()

    # change something
    passfile.pass_object.organizationName = "new organization"

    with pytest.raises(crypto.VerificationError):
        passfile.verify()

    #now sign it, so verification should pass now
    passfile._sign(common.key_file, common.cert_file, common.wwdr_file)
    passfile.verify()

    zipfile = passfile._as_zip()
    assert zipfile

    crypto.verify_manifest(passfile.files["manifest.json"], passfile.files["signature"])


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_passbook_creation():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """

    passfile = create_shell_pass()
    passfile._add_file("icon.png", open(common.resources / "white_square.png", "rb"))
    passfile._sign(common.key_file, common.cert_file, common.wwdr_file)
    zipfile = passfile._as_zip()
    # zipfile = passfile.create(common.cert_file, common.key_file, common.wwdr_file, None)
    assert zipfile


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_passbook_creation_integration(generated_passes_dir):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = generated_passes_dir / "basic_pass.pkpass"
    passfile = create_shell_pass(
        passTypeIdentifier="pass.demo.lmu.de", teamIdentifier="JG943677ZY"
    )
    passfile._add_file("icon.png", open(resources / "white_square.png", "rb"))

    passfile._sign(
        certs / "private" / "private.key",
        certs / "private" / "certificate.pem",
        certs / "private" / "wwdr_certificate.pem",
    )

    with open(pass_file_name, "wb") as fh:
        fh.write(passfile._as_zip().getvalue())
    os.system("open " + str(pass_file_name))


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_passbook_creation_integration_loyalty_with_nfc(generated_passes_dir):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = generated_passes_dir / "loyaltypass_nfc.pkpass"

    sn = uuid.uuid4().hex
    cardInfo = StoreCard()
    cardInfo.addHeaderField("title", "EAIE2023NFC", "")
    # if name:
    #     cardInfo.addSecondaryField("name", name, "")
    stdBarcode = Barcode(message=sn, format=BarcodeFormat.CODE128, altText=sn)
    passobject = Pass(
        storeCard=cardInfo,
        organizationName="eduTAP",
        passTypeIdentifier="pass.demo.lmu.de",
        teamIdentifier="JG943677ZY",
        serialNumber=sn,
        description="edutap Sample Pass",
    )

    passobject.barcode = stdBarcode

    passfile = PkPass(pass_object=passobject)

    passfile._add_file("icon.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("icon@2x.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("icon@3x.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("logo.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("logo@2x.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("strip.png", open(resources / "eaie-hero.jpg", "rb"))

    passobject.backgroundColor = "#fa511e"
    passobject.nfc = NFC(
        message="Hello NFC",
        encryptionPublicKey="MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgACWpF1zC3h+dCh+eWyqV8unVddh2LQaUoV8LQrgb3BKkM=",
        # "MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgAC0utmUaTA6mrvZoALBTpaKI0xIoQxHXtWj37OtiSttY4="
        requiresAuthentication=False,
    )

    passfile._sign(
        certs / "private" / "private.key",
        certs / "private" / "certificate.pem",
        certs / "private" / "wwdr_certificate.pem",
    )
    with open(pass_file_name, "wb") as fh:
        fh.write(passfile._as_zip().getvalue())
        os.system("open " + str(pass_file_name))


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_passbook_creation_integration_eventticket(generated_passes_dir):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = generated_passes_dir / "eventticket.pkpass"

    cardInfo = EventTicket()
    cardInfo.addPrimaryField("title", "EAIE2023", "event")
    stdBarcode = Barcode(
        message="test barcode", format=BarcodeFormat.CODE128, altText="alternate text"
    )
    sn = uuid.uuid4().hex
    passobject = Pass(
        eventTicket=cardInfo,
        organizationName="eduTAP",
        passTypeIdentifier="pass.demo.lmu.de",
        teamIdentifier="JG943677ZY",
        serialNumber=sn,
        description="edutap Sample Pass",
        webServiceURL="https://edutap.bluedynamics.net:8443/apple_update_service/v1",
        authenticationToken="0123456789012345",  # must be 16 characters
    )

    passobject.barcode = stdBarcode
    passfile = PkPass(pass_object=passobject)

    passfile._add_file("icon.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("iconx2.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("logo.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("logox2.png", open(resources / "edutap.png", "rb"))
    passfile._add_file("strip.png", open(resources / "eaie-hero.jpg", "rb"))
    # passfile.addFile("background.png", open(resources / "eaie-hero.jpg", "rb"))

    passobject.backgroundColor = "#fa511e"
    passfile._sign(
        certs / "private" / "private.key",
        certs / "private" / "certificate.pem",
        certs / "private" / "wwdr_certificate.pem",
    )

    with open(pass_file_name, "wb") as fh:
        fh.write(passfile._as_zip().getvalue())
        os.system("open " + str(pass_file_name))


@only_test_if_crypto_supports_verification
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_open_pkpass_and_sign_again(apple_passes_dir, generated_passes_dir):
    """
    tests an existing pass not created by this library and signs it again
    this pass comes as demo from apple and the pass.json contains
    trailing commas which are not allowed in json, but apple accepts
    them, so we have to tolerate them as well
    """
    fn = apple_passes_dir / "BoardingPass.pkpass"
    with open(fn, "rb") as fh:
        pkpass = PkPass.from_zip(fn)

        assert pkpass

    crypto.verify_manifest(pkpass.files["manifest.json"], pkpass.files["signature"])
    pkpass.pass_object.passInformation.secondaryFields[0].value = "John Doe"
    newname = "BoardingPass_signed.pkpass"
    
    # the following 2 lines are crucial for us being able to sign the pass
    # the passTypeIdentifier and teamIdentifier must match with the certificate
    pkpass.pass_object.passTypeIdentifier = "pass.demo.lmu.de"
    pkpass.pass_object.teamIdentifier = "JG943677ZY"
    
    with open(generated_passes_dir / newname, "wb") as fh:
        pkpass._sign(
            common.certs / "private" / "private.key",
            common.certs / "private" / "certificate.pem",
            common.certs / "private" / "wwdr_certificate.pem",
        )
        fh.write(pkpass._as_zip().getvalue())

    crypto.verify_manifest(pkpass.files["manifest.json"], pkpass.files["signature"])

    os.system("open " + str(generated_passes_dir / newname))


@pytest.mark.integration
def test_connect_apple_apn_sandbox_server():
    """
    establish a connection to the sandbox APN server using your
    apple certificates and private key.
    """
