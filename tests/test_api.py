# pylint: disable=redefined-outer-name
from common import apple_passes_dir
from common import generated_passes_dir
from common import key_files_exist
from common import only_test_if_crypto_supports_verification
from common import settings_test
from edutap.wallet_apple import api
from edutap.wallet_apple.crypto import VerificationError
from edutap.wallet_apple.settings import Settings

import common
import os
import pytest


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
    assert pkpass is not None


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
def test_sign_existing_pass(
    apple_passes_dir, generated_passes_dir, settings_test: Settings
):
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        pkpass.pass_object.passTypeIdentifier = settings_test.pass_type_identifier
        pkpass.pass_object.teamIdentifier = settings_test.team_identifier
        pkpass.pass_object.passInformation.secondaryFields[0].value = "Doald Duck"

        api.sign(pkpass, settings=settings_test)
        assert pkpass.is_signed

        ofile = generated_passes_dir / "BoardingPass-signed1.pkpass"
        with api.pkpass(pkpass) as zip_fh:
            with open(ofile, "wb") as fh:
                fh.write(zip_fh.read())

        os.system(f"open {ofile}")


@only_test_if_crypto_supports_verification
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
def test_sign_and_verify_pass(apple_passes_dir, settings_test: Settings):
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        # this pass has not been created and signed by us, so we verify
        # it without recomputing the manifest
        api.verify(pkpass, recompute_manifest=False)

        # when we change the pass, the verification should fail
        pkpass.pass_object.passInformation.secondaryFields[0].value = "John Doe"

        # we have to change the passTypeIdentifier and teamIdentifier
        # so that we can sign it with our key and certificate
        pkpass.pass_object.passTypeIdentifier = settings_test.pass_type_identifier
        pkpass.pass_object.teamIdentifier = settings_test.team_identifier

        # now of course the verification should fail
        with pytest.raises(VerificationError) as ex:
            api.verify(pkpass)
            assert "pass is not verified" in str(ex)

        # now we sign the pass and the verification should pass
        api.sign(pkpass, settings=settings_test)
        api.verify(pkpass, settings=settings_test)
        assert pkpass.is_signed
