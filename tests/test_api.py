import pytest
from edutap.wallet_apple import api
import common


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
            assert "only either 'data' or 'file' may be provided, both is not allowed" in str(ex)


def test_new_pass_empty():
    pkpass = api.new()

