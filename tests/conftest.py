from edutap.wallet_apple import crypto
from edutap.wallet_apple.models.passes import Barcode
from edutap.wallet_apple.models.passes import BarcodeFormat
from edutap.wallet_apple.models.passes import Coupon
from edutap.wallet_apple.models.passes import Pass
from edutap.wallet_apple.models.passes import PkPass
from edutap.wallet_apple.models.passes import StoreCard
from edutap.wallet_apple.settings import Settings
from importlib import metadata
from pathlib import Path
from typing import Callable

import os
import platform
import pytest
import subprocess
import tempfile
import uuid


cwd = Path(__file__).parent
data = cwd / "data"
jsons = data / "jsons"
resources = data / "resources"
certs = data / "certs"
password_file = certs / "password.txt"
cert_file = certs / "private" / "certificate.pem"
key_file = certs / "private" / "private.key"
wwdr_file = certs / "private" / "wwdr_certificate.pem"

PASS_TYPE_IDENTIFIER = "pass.demo.lmu.de"


def load_pass_viewer(passfile: Path) -> None:
    """
    open the pass file in the pass viewer,
    under MacOS the pass viewer only opensif the pass is vald.

    uses the security cms command to verify the pass file

    see https://medium.com/deutsche-telekom-gurgaon/safeguarding-data-using-der-encoded-cms-message-0ce156946369
    see https://ss64.com/mac/security.html
    """
    # os.system(f"open {passfile}")  #uncomment this line to open the pass file in the pass viewer for visual inspection

    if platform.system() == "Darwin":
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temporäres Verzeichnis erstellt: {temp_dir}")

            odir = Path(temp_dir)

            os.system(f"unzip -o {passfile} -d {odir}")

            result = subprocess.run(
                ["security", "cms", "-D", "-i", odir / "signature"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if result.returncode != 0:
                raise ValueError(result.stderr)

            with open(odir / "manifest.json", "rb") as fh:
                manifest = fh.read()

            if manifest != result.stdout:
                raise ValueError("manifest and signature do not match")

            result.returncode == 0


@pytest.fixture
def generated_passes_dir():
    target = data / "generated_passes"
    os.makedirs(target, exist_ok=True)
    return target


@pytest.fixture
def apple_passes_dir():
    target = data / "apple_passes"
    # os.makedirs(target, exist_ok=True)
    return target


@pytest.fixture
def passes_json_dir():
    target = data / "jsons"
    # os.makedirs(target, exist_ok=True)
    return target


@pytest.fixture
def settings_test():
    settings = Settings(
        root_dir=cwd / "data",
        cert_dir_relative="certs/private",
        team_identifier="JG943677ZY",
    )

    return settings


@pytest.fixture(scope="function")
def testlog():
    """
    create a logging handler that stores the log messages into a list
    this logging handler will configured into logger
    """
    from structlog.testing import capture_logs  # type: ignore

    with capture_logs() as logs:
        logs.clear()
        yield logs
        logs.clear()
        return logs


@pytest.fixture(scope="function")
def testlog_empty():
    """
    create a logging handler that stores the log messages into a list
    this logging handler will configured into logger
    """
    from structlog.testing import capture_logs  # type: ignore

    with capture_logs() as logs:
        logs.clear()
        yield logs
        logs.clear()
        return logs


def key_files_exist():
    """
    utility function to check if the key files exist
    called by pytest.skipif for the integration tests
    """
    settings = Settings(
        root_dir=cwd / "data",
        cert_dir_relative="certs/private",
        pass_type_identifier="pass.demo.lmu.de",
        team_identifier="JG943677ZY",
    )

    return (
        os.path.exists(settings.private_key)
        # and os.path.exists(settings.certificate)
        and os.path.exists(settings.wwdr_certificate)
    )


def only_test_if_crypto_supports_verification(func):
    """decorator to skip tests if cryptography is not installed"""
    if crypto.supports_verification():
        return func
    return pytest.mark.skip("pycryptography support for verification missing")(func)


def create_shell_pass(
    barcodeFormat=BarcodeFormat.CODE128,
    passTypeIdentifier=PASS_TYPE_IDENTIFIER,
    teamIdentifier="Team Identifier",
):
    cardInfo = StoreCard()
    cardInfo.addPrimaryField("name", "Jähn Doe", "Name")
    stdBarcode = Barcode(
        message="test barcode", format=barcodeFormat, altText="alternate text"
    )
    pass_object = Pass(
        storeCard=cardInfo,
        organizationName="Org Name",
        passTypeIdentifier=passTypeIdentifier,
        teamIdentifier=teamIdentifier,
        serialNumber="1234567",
        description="A Sample Pass",
    )
    pass_object.barcode = stdBarcode
    pkpass = PkPass(pass_object=pass_object)
    return pkpass


def create_shell_pass_loyalty(
    barcodeFormat=BarcodeFormat.CODE128,
    passTypeIdentifier=PASS_TYPE_IDENTIFIER,
    teamIdentifier="Team Identifier",
):
    cardInfo = Coupon()
    cardInfo.addPrimaryField("name", "Jähn Doe", "Name")
    stdBarcode = Barcode(
        message="test barcode", format=barcodeFormat, altText="alternate text"
    )
    sn = uuid.uuid4().hex
    passfile = Pass(
        coupon=cardInfo,
        organizationName="eduTAP",
        passTypeIdentifier=passTypeIdentifier,
        teamIdentifier=teamIdentifier,
        serialNumber=sn,
        description="edutap Sample Pass",
    )

    # passfile.passInformation.primaryFields.append(
    #     Field(key="balance", label="Balance", value="100", currencyCode="EUR")
    # )
    # passfile.passInformation.secondaryFields.append(
    #     Field(key="points", label="Points", value="101")
    # )
    # passfile.passInformation.backFields.append(
    #     Field(key="terms", label="Terms", value="Terms and Conditions")
    # )

    passfile.barcode = stdBarcode
    return passfile


@pytest.fixture
def entrypoints_testing(monkeypatch) -> Callable:
    """
    fixture for mocking entrypoints for testing:

    - class TestPassRegistration
    - class TestPassDataAcquisition
    - class TestLogging
    """
    eps = {
        "edutap.wallet_apple.plugins": [
            metadata.EntryPoint(
                name="PassRegistration",
                value="plugins:TestPassRegistration",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            metadata.EntryPoint(
                name="PassRegistration",
                value="plugins:TestPassRegistration2",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            metadata.EntryPoint(
                name="PassDataAcquisition",
                value="plugins:TestPassDataAcquisition",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            metadata.EntryPoint(
                name="Logging",
                value="plugins:TestLogging",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            metadata.EntryPoint(
                name="Logging",
                value="plugins:TestLogging2",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
        ]
    }

    def mock_entry_points(group: str):
        """
        replacement for the official `importlib.metadata.entry_points()` function
        """
        return eps.get(group, [])

    from edutap.wallet_apple import plugins

    monkeypatch.setattr(metadata, "entry_points", mock_entry_points)
    monkeypatch.setattr(plugins, "entry_points", mock_entry_points)
    return mock_entry_points


@pytest.fixture
def pass_data_passthrough(monkeypatch):
    """
    fixture patch env with apple_passdata_passthrough
    """
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_PASS_DATA_PASSTHROUGH",
        "true",
    )
