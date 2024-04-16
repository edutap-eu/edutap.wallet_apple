from common import certs
from common import create_shell_pass
from common import resources
from edutap.wallet_apple.models import Barcode
from edutap.wallet_apple.models import BarcodeFormat
from edutap.wallet_apple.models import EventTicket
from edutap.wallet_apple.models import NFC
from edutap.wallet_apple.models import Pass
from edutap.wallet_apple.models import StoreCard

import os
import pytest
import uuid


@pytest.mark.integration
def test_passbook_creation_integration():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = "/Users/phil/dev/projects/edutap/apple/passes/pass1.pkpass"
    passfile = create_shell_pass(
        passTypeIdentifier="pass.demo.lmu.de", teamIdentifier="JG943677ZY"
    )
    passfile.addFile("icon.png", open(resources / "white_square.png", "rb"))

    zip = passfile.create(
        certs / "private" / "certificate.pem",
        certs / "private" / "private.key",
        certs / "private" / "wwdr_certificate.pem",
        "",
    )

    open(pass_file_name, "wb").write(zip.getvalue())
    os.system("open " + pass_file_name)


@pytest.mark.integration
def test_passbook_creation_integration_loyalty_with_nfc():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = "/Users/phil/dev/projects/edutap/apple/passes/pass1.pkpass"

    sn = uuid.uuid4().hex
    cardInfo = StoreCard()
    cardInfo.addHeaderField("title", "EAIE2023", "")
    # if name:
    #     cardInfo.addSecondaryField("name", name, "")
    stdBarcode = Barcode(message=sn, format=BarcodeFormat.CODE128, altText=sn)
    passfile = Pass(
        storeCard=cardInfo,
        organizationName="eduTAP",
        passTypeIdentifier="pass.demo.lmu.de",
        teamIdentifier="JG943677ZY",
        serialNumber=sn,
        description="edutap Sample Pass",
    )

    passfile.barcode = stdBarcode

    passfile.addFile("icon.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("icon@2x.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("icon@3x.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("logo.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("logo@2x.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("strip.png", open(resources / "eaie-hero.jpg", "rb"))

    passfile.backgroundColor = "#fa511e"
    passfile.nfc = NFC(
        message="Hello NFC",
        encryptionPublicKey="MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgACWpF1zC3h+dCh+eWyqV8unVddh2LQaUoV8LQrgb3BKkM=",
        # "MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgAC0utmUaTA6mrvZoALBTpaKI0xIoQxHXtWj37OtiSttY4="
        requiresAuthentication=False,
    )

    zip = passfile.create(
        certs / "private" / "certificate.pem",
        certs / "private" / "private.key",
        certs / "private" / "wwdr_certificate.pem",
        "",
    )
    open(pass_file_name, "wb").write(zip.getvalue())
    os.system("open " + pass_file_name)


@pytest.mark.integration
def test_passbook_creation_integration_eventticket():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.

    ATTENTION: in order to run this test you have to install the necessary certificates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.

    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = "/Users/phil/dev/projects/edutap/apple/passes/pass1.pkpass"

    cardInfo = EventTicket()
    cardInfo.addPrimaryField("title", "EAIE2023", "event")
    stdBarcode = Barcode(
        message="test barcode", format=BarcodeFormat.CODE128, altText="alternate text"
    )
    sn = uuid.uuid4().hex
    passfile = Pass(
        eventTicket=cardInfo,
        organizationName="eduTAP",
        passTypeIdentifier="pass.demo.lmu.de",
        teamIdentifier="JG943677ZY",
        serialNumber=sn,
        description="edutap Sample Pass",
    )

    passfile.barcode = stdBarcode

    passfile.addFile("icon.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("iconx2.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("logo.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("logox2.png", open(resources / "edutap.png", "rb"))
    passfile.addFile("strip.png", open(resources / "eaie-hero.jpg", "rb"))
    # passfile.addFile("background.png", open(resources / "eaie-hero.jpg", "rb"))

    passfile.backgroundColor = "#fa511e"
    zip = passfile.create(
        certs / "private" / "certificate.pem",
        certs / "private" / "private.key",
        certs / "private" / "wwdr_certificate.pem",
        "",
    )

    open(pass_file_name, "wb").write(zip.getvalue())
    os.system("open " + pass_file_name)


@pytest.mark.integration
def test_connect_apple_apn_sandbox_server():
    """
    establish a connection to the sandbox APN server using your
    apple certificates and private key.
    """
