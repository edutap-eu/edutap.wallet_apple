# pylint: disable=redefined-outer-name
# pylint: disable=unused-imports

from conftest import key_files_exist
from conftest import load_pass_viewer
from conftest import only_test_if_crypto_supports_verification
from edutap.wallet_apple import api
from edutap.wallet_apple.crypto import VerificationError
from edutap.wallet_apple.settings import Settings
from io import BytesIO
from plugins import SettingsTest

import conftest as conftest
import json
import pytest


settings = SettingsTest()


def test_load_pass_from_json():
    with open(conftest.jsons / "minimal_storecard.json", encoding="utf-8") as fh:
        buf = fh.read()
        data = json.loads(buf)
        pkpass = api.new(data=data)
        assert pkpass is not None


@pytest.mark.parametrize(
    "json_file", ["semantic-fields-pass.json", "semantic-fields-pass1.json"]
)
def test_load_pass_with_extra_fields_from_json(json_file: str, settings_test: Settings):
    """
    test if the pass has fields not
    specified in the pass schema attributes
    in this case a field named 'semantics'
    """
    with open(conftest.jsons / json_file, encoding="utf-8") as fh:
        buf = fh.read()
        data = json.loads(buf)
        pkpass = api.new(data=data)
        semantics = getattr(pkpass.pass_object, "semantics")
        assert semantics is not None
        if (
            conftest.key_files_exist()
            and pkpass.pass_object_safe.passTypeIdentifier
            in settings_test.get_available_passtype_ids()
        ):
            api.sign(pkpass, settings=settings_test)
        assert pkpass is not None


def test_load_pass_from_zip():
    with open(conftest.resources / "basic_pass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        assert pkpass is not None


def test_load_pass_with_data_and_file_must_fail():
    with open(conftest.jsons / "minimal_storecard.json", encoding="utf-8") as fh:
        buf = fh.read()

    with open(conftest.resources / "basic_pass.pkpass", "rb") as fh:
        with pytest.raises(ValueError) as ex:
            pkpass = api.new(data=buf, file=fh)
            assert pkpass is not None
            assert (
                "only either 'data' or 'file' may be provided, both is not allowed"
                in str(ex)
            )


def test_new_pass_empty():
    pkpass = api.new()
    assert pkpass is not None


def test_create_and_save_unsigned_pass_from_json_dict(
    generated_passes_dir,
):
    """
    creates a pass object from dict, adds a file and saves it to a pkpass file.
    checks if pass.json and the added file are in the pkpass file.
    """
    buf = open(conftest.jsons / "storecard_with_nfc.json").read()
    jdict = json.loads(buf)
    pass1 = api.new(data=jdict)

    pass1._add_file("icon.png", open(conftest.resources / "white_square.png", "rb"))

    ofile = generated_passes_dir / "unsigned-pass.pkpass"
    with api.pkpass(pass1) as zip_fh:
        with open(ofile, "wb") as fh:
            fh.write(zip_fh.read())

    # check if the files are in the generated pkpass
    with open(ofile, "rb") as fh:
        pkpass = api.new(file=fh)
        assert "pass.json" in pkpass.files
        assert "icon.png" in pkpass.files

        # check if the manifest and signature are not in the generated pkpass
        # since the pass is not signed yet
        assert "manifest.json" not in pkpass.files
        assert "signature" not in pkpass.files


@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_sign_existing_pass_and_get_bytes_io(
    apple_passes_dir, generated_passes_dir, settings_test: Settings, pass_type_id: str
):
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        pkpass.pass_object_safe.passTypeIdentifier = pass_type_id
        pkpass.pass_object_safe.teamIdentifier = settings_test.team_identifier
        pkpass.pass_object_safe.pass_information.secondaryFields[0].value = (
            "Donald Duck"
        )

        api.sign(pkpass, settings=settings_test)
        assert pkpass.is_signed

        ofile = generated_passes_dir / "BoardingPass-signed1.pkpass"
        with api.pkpass(pkpass) as zip_fh:
            with open(ofile, "wb") as fh1:
                fh1.write(zip_fh.read())

        load_pass_viewer(ofile)


@only_test_if_crypto_supports_verification
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
@pytest.mark.integration
def test_sign_and_verify_pass(
    apple_passes_dir, settings_test: Settings, pass_type_id: str
):
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        # this pass has not been created and signed by us, so we verify
        # it without recomputing the manifest
        api.verify(pkpass, recompute_manifest=False)

        # when we change the pass, the verification should fail
        pkpass.pass_object_safe.pass_information.secondaryFields[0].value = "John Doe"

        # we have to change the passTypeIdentifier and teamIdentifier
        # so that we can sign it with our key and certificate
        pkpass.pass_object_safe.passTypeIdentifier = pass_type_id
        pkpass.pass_object_safe.teamIdentifier = settings_test.team_identifier

        # now of course the verification should fail
        with pytest.raises(VerificationError) as ex:
            api.verify(pkpass)
            assert "pass is not verified" in str(ex)

        # now we sign the pass and the verification should pass
        api.sign(pkpass, settings=settings_test)
        api.verify(pkpass, settings=settings_test)
        assert pkpass.is_signed


@pytest.mark.skip("wait for pydantic fix")
@pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
def test_serialize_existing_pass_as_json_dict(
    apple_passes_dir, generated_passes_dir, settings_test: Settings, pass_type_id: str
):
    """
    tests serialization of a pass to a BytesIO object.

    Since there is a strange behavior in pydantic concerning serialization of
    file objects:
        https://github.com/pydantic/pydantic/issues/8907#issuecomment-2550673061

    This test only works if the resulting BytesIO object is not wrapped in a
    SerializationIterator object
    """
    with open(apple_passes_dir / "BoardingPass.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        pkpass.pass_object_safe.passTypeIdentifier = pass_type_id
        pkpass.pass_object_safe.teamIdentifier = settings_test.team_identifier
        pkpass.pass_object_safe.pass_information.secondaryFields[0].value = (
            "Donald Duck"
        )

        api.sign(pkpass, settings=settings_test)
        assert pkpass.is_signed

        d = pkpass.model_dump(mode="BytesIO")

        assert isinstance(d, BytesIO)
        print(d)


# @pytest.mark.skipif(not key_files_exist(), reason="key files are missing")
@pytest.mark.integration
@pytest.mark.parametrize("pass_type_id", settings.get_available_passtype_ids())
def test_sign_existing_generic_pass_and_get_bytes_io(
    apple_passes_dir,
    generated_passes_dir,
    settings_test: Settings,
    pass_type_id: str,
):
    with open(settings_test.root_dir / "unsigned-passes" / "1234.pkpass", "rb") as fh:
        pkpass = api.new(file=fh)
        pkpass.pass_object_safe.passTypeIdentifier = pass_type_id
        pkpass.pass_object_safe.teamIdentifier = settings_test.team_identifier

        fernet_key = b"AIYbyKUTkJpExGmNjEoI23AOqcMHIO7HhWPnMYKQWZA="  # TODO: softcode
        settings_test.fernet_key = fernet_key.decode("utf-8")
        token = api.create_auth_token(
            pkpass.pass_object_safe.passTypeIdentifier,
            "1234",  # TODO: serial number softcoded,
            fernet_key=fernet_key,
        )
        pkpass.pass_object_safe.authenticationToken = token.decode("utf-8")
        pkpass.pass_object_safe.serialNumber = "1234"
        pkpass.pass_object_safe.webServiceURL = api.save_link(
            pkpass.pass_object_safe.passTypeIdentifier,
            pkpass.pass_object_safe.serialNumber,
            settings=settings_test,
        )
        api.sign(pkpass, settings=settings_test)
        assert pkpass.is_signed

        ofile = generated_passes_dir / "1234.pkpass"
        with api.pkpass(pkpass) as zip_fh:
            with open(ofile, "wb") as fh1:
                fh1.write(zip_fh.read())

        load_pass_viewer(ofile)
