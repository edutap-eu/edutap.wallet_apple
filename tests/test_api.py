# pylint: disable=redefined-outer-name
import os
import pytest
from edutap.wallet_apple import api
import common
from common import (
    generated_passes_dir,
    apple_passes_dir,
    only_test_if_crypto_supports_verification,
    settings_test,
)
from edutap.wallet_apple.crypto import VerificationError
from edutap.wallet_apple.settings import Settings


def test_load_pass_from_json():
    with open(common.jsons / "minimal_storecard.json", encoding="utf-8") as fh:
        buf = fh.read()
        pkpass = api.new(data=buf)
        assert pkpass is not None


def test_load_pass_from_zip():
    with open(common.resources / "basic_pass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        assert pkpass is not None


def test_load_pass_with_data_and_file_must_fail():
    with open(common.jsons / "minimal_storecard.json", encoding="utf-8") as fh:
        buf = fh.read()

    with open(common.resources / "basic_pass.pkpass", "rb") as fh:
        with pytest.raises(ValueError) as ex:
            pkpass = api.new(data=buf, file=fh)
            assert (
                "only either 'data' or 'file' may be provided, both is not allowed"
                in str(ex)
            )


def test_new_pass_empty():
    pkpass = api.new()


def test_sign_existing_pass(
    apple_passes_dir, generated_passes_dir, settings_test: Settings
):
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        pkpass.pass_object.passTypeIdentifier = settings_test.pass_type_identifier
        pkpass.pass_object.teamIdentifier = settings_test.team_identifier
        api.sign(pkpass, settings=settings_test)
        assert pkpass.is_signed

        
        ofile = generated_passes_dir / "BoardingPass-signed.pkpass"
        with api.pkpass(pkpass) as zip_fh:
            with open(ofile, "wb") as fh:
                fh.write(zip_fh.getvalue())
                
        os.system(f"open {ofile}")


@only_test_if_crypto_supports_verification
@pytest.mark.integration
def test_sign_and_verify_pass(apple_passes_dir, settings_test: Settings):
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        api.verify(pkpass, recompute_manifest=False)
        pkpass.pass_object.passInformation.secondaryFields[0].value = "John Doe"
        pkpass.pass_object.passTypeIdentifier = settings_test.pass_type_identifier
        pkpass.pass_object.teamIdentifier = settings_test.team_identifier

        with pytest.raises(VerificationError) as ex:
            api.verify(pkpass)
            assert "pass is not verified" in str(ex)

        api.sign(pkpass, settings=settings_test)
        api.verify(pkpass, settings=settings_test)
        # assert pkpass.is_signed()
