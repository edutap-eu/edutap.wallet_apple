import platform
from conftest import certs
from conftest import create_shell_pass
from conftest import key_files_exist
from conftest import load_pass_viewer
from conftest import only_test_if_crypto_supports_verification
from conftest import resources
from edutap.wallet_apple import crypto
from edutap.wallet_apple.models.passes import Barcode
from edutap.wallet_apple.models.passes import BarcodeFormat
from edutap.wallet_apple.models.passes import EventTicket
from edutap.wallet_apple.models.passes import NFC
from edutap.wallet_apple.models.passes import Pass
from edutap.wallet_apple.models.passes import PkPass
from edutap.wallet_apple.models.passes import StoreCard
from plugins import SettingsTest

import conftest
import json
import pytest
import uuid


settings = SettingsTest()


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_get_available_pass_type_ids(settings_test):
    ids = settings_test.get_available_passtype_ids()
    assert "pass.demo.lmu.de" in ids


@only_test_if_crypto_supports_verification
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_signing(settings_test, pass_type_id):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """

    passfile = create_shell_pass()
    manifest_json = passfile._create_manifest()

    key, cert, wwdr_cert = crypto.load_key_files(
        conftest.key_file,
        settings_test.get_certificate_path(pass_type_id),
        conftest.wwdr_file,
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


@only_test_if_crypto_supports_verification
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_signing1(settings_test, pass_type_id):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """

    passfile = create_shell_pass()
    manifest_json = passfile._create_manifest()
    cert_file = settings_test.get_certificate_path(pass_type_id)

    key, cert, wwdr_cert = crypto.load_key_files(
        conftest.key_file,
        cert_file,
        conftest.wwdr_file,
    )

    signature = crypto.sign_manifest(
        manifest_json,
        key,
        cert,
        wwdr_cert,
    )

    crypto.verify_manifest(manifest_json, signature)
    # tamper manifest by changing an attribute
    passfile.pass_object.organizationName = "new organization"
    tampered_manifest = passfile._create_manifest()

    # Verification MUST fail!
    with pytest.raises(crypto.VerificationError):
        crypto.verify_manifest(tampered_manifest, signature)

    passfile = create_shell_pass()
    passfile._add_file("icon.png", open(conftest.resources / "white_square.png", "rb"))
    passfile.sign(conftest.key_file, cert_file, conftest.wwdr_file)

    zipfile = passfile.as_zip_bytesio()
    assert zipfile is not None


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@only_test_if_crypto_supports_verification
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_verification(settings_test, pass_type_id):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)

    passfile = create_shell_pass()
    passfile._add_file("icon.png", open(conftest.resources / "white_square.png", "rb"))
    passfile.sign(conftest.key_file, cert_file, conftest.wwdr_file)
    manifest = passfile._create_manifest()
    signature = passfile.files["signature"]
    crypto.verify_manifest(manifest, signature)
    passfile.verify()

    # change something
    passfile.pass_object.organizationName = "new organization"

    with pytest.raises(crypto.VerificationError):
        passfile.verify()

    # now sign it, so verification should pass now
    passfile.sign(conftest.key_file, cert_file, conftest.wwdr_file)
    passfile.verify()

    zipfile = passfile.as_zip_bytesio()
    assert zipfile

    crypto.verify_manifest(passfile.files["manifest.json"], passfile.files["signature"])


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_passbook_creation(settings_test, pass_type_id):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)

    passfile = create_shell_pass()
    passfile._add_file("icon.png", open(conftest.resources / "white_square.png", "rb"))
    passfile.sign(conftest.key_file, cert_file, conftest.wwdr_file)
    zipfile = passfile.as_zip_bytesio()
    # zipfile = passfile.create(common.cert_file, common.key_file, common.wwdr_file, None)
    assert zipfile


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_passbook_creation_integration(
    generated_passes_dir, settings_test, pass_type_id
):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)

    pass_file_name = generated_passes_dir / "basic_pass.pkpass"
    passfile = create_shell_pass(
        passTypeIdentifier="pass.demo.lmu.de", teamIdentifier="JG943677ZY"
    )
    passfile._add_file("icon.png", open(resources / "white_square.png", "rb"))

    passfile.sign(
        certs / "private" / "private.key",
        cert_file,
        certs / "private" / "wwdr_certificate.pem",
    )

    with open(pass_file_name, "wb") as fh:
        fh.write(passfile.as_zip_bytesio().getvalue())
    load_pass_viewer(pass_file_name)


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_passbook_creation_integration_loyalty_with_nfc(
    generated_passes_dir, settings_test, pass_type_id
):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)
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

    passfile.sign(
        certs / "private" / "private.key",
        cert_file,
        certs / "private" / "wwdr_certificate.pem",
    )
    with open(pass_file_name, "wb") as fh:
        fh.write(passfile.as_zip_bytesio().getvalue())
        load_pass_viewer(pass_file_name)


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_passbook_creation_integration_eventticket(
    generated_passes_dir, settings_test, pass_type_id
):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)
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
    passfile.sign(
        certs / "private" / "private.key",
        cert_file,
        certs / "private" / "wwdr_certificate.pem",
    )

    with open(pass_file_name, "wb") as fh:
        fh.write(passfile.as_zip_bytesio().getvalue())
        load_pass_viewer(pass_file_name)


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.skipif(platform.system() != "Darwin", reason="tampering with the manifest is not possible")
@pytest.mark.integration
def test_passbook_creation_integration_eventticket_unsigned(
    generated_passes_dir, settings_test, pass_type_id
):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """
    pass_file_name = generated_passes_dir / "eventticket-invalid.pkpass"

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

    with pytest.raises(ValueError):
        with open(pass_file_name, "wb") as fh:
            fh.write(passfile.as_zip_bytesio().getvalue())
            load_pass_viewer(pass_file_name)


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.skipif(platform.system() != "Darwin", reason="tampering with the manifest is not possible")
@pytest.mark.integration
def test_passbook_creation_integration_eventticket_tampered(
    generated_passes_dir, settings_test, pass_type_id
):
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)
    pass_file_name = generated_passes_dir / "eventticket-tampered.pkpass"

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
    passfile.sign(
        certs / "private" / "private.key",
        cert_file,
        certs / "private" / "wwdr_certificate.pem",
    )

    # tamper with the manifest
    manifest = json.loads(passfile.files["manifest.json"])
    passfile.files["pass.json"] = passfile.pass_object.model_dump_json(indent=4)
    manifest["pass.json"] = "tampered"
    passfile.files["manifest.json"] = passfile.files["manifest.json"] = json.dumps(
        manifest
    )

    with pytest.raises(ValueError):
        with open(pass_file_name, "wb") as fh:
            fh.write(passfile.as_zip_bytesio().getvalue())
            load_pass_viewer(pass_file_name)


@only_test_if_crypto_supports_verification
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_open_pkpass_and_sign_again(
    apple_passes_dir, generated_passes_dir, settings_test, pass_type_id
):
    """
    tests an existing pass not created by this library and signs it again
    this pass comes as demo from apple and the pass.json contains
    trailing commas which are not allowed in json, but apple accepts
    them, so we have to tolerate them as well
    """
    cert_file = settings_test.get_certificate_path(pass_type_id)

    fn = apple_passes_dir / "BoardingPass.pkpass"
    with open(fn, "rb") as fh:
        pkpass = PkPass.from_zip(fn)
        assert pkpass

    crypto.verify_manifest(pkpass.files["manifest.json"], pkpass.files["signature"])
    pkpass.pass_object.pass_information.secondaryFields[0].value = "John Doe"
    newname = "BoardingPass_signed.pkpass"

    # the following 2 lines are crucial for us being able to sign the pass
    # the passTypeIdentifier and teamIdentifier must match with the certificate
    pkpass.pass_object.passTypeIdentifier = "pass.demo.lmu.de"
    pkpass.pass_object.teamIdentifier = "JG943677ZY"

    with open(generated_passes_dir / newname, "wb") as fh:
        pkpass.sign(
            conftest.certs / "private" / "private.key",
            cert_file,
            conftest.certs / "private" / "wwdr_certificate.pem",
        )
        fh.write(pkpass.as_zip_bytesio().getvalue())

    crypto.verify_manifest(pkpass.files["manifest.json"], pkpass.files["signature"])

    load_pass_viewer(generated_passes_dir / newname)


@pytest.mark.integration
def test_connect_apple_apn_sandbox_server():
    """
    establish a connection to the sandbox APN server using your
    apple certificates and private key.
    """
