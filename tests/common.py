from pathlib import Path

from edutap.wallet_apple.models import Barcode, BarcodeFormat, Pass, StoreCard


cwd = Path(__file__).parent
data = cwd / "data"
jsons = data / "jsons"
resources = data / "resources"
certs = data / "certs"
password_file = certs / "password.txt"
cert_file = certs / "certificate.pem"
key_file = certs / "private.key"
wwdr_file = certs / "wwdr_certificate.pem"


def create_shell_pass(barcodeFormat=BarcodeFormat.CODE128):
    cardInfo = StoreCard()
    cardInfo.addPrimaryField("name", "Jähn Doe", "Name")
    stdBarcode = Barcode(
        message="test barcode", format=barcodeFormat, altText="alternate text"
    )
    passfile = Pass(
        storeCard=cardInfo,
        organizationName="Org Name",
        passTypeIdentifier="Pass Type ID",
        teamIdentifier="Team Identifier",
        serialNumber="1234567",
        description="A Sample Pass",
    )
    passfile.barcode = stdBarcode
    passfile.serialNumber = "1234567"
    passfile.description = "A Sample Pass"
    return passfile
