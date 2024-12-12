from common import create_shell_pass
from edutap.wallet_apple.models import passes
from edutap.wallet_apple.models.passes import BarcodeFormat

import common
import json


def test_model():
    pass1 = passes.PassInformation(
        headerFields=[
            passes.Field(key="header1", value="header1", label="header1"),
        ]
    )

    print(pass1.model_dump(exclude_none=True))


def test_load_minimal_storecard():
    buf = open(common.jsons / "minimal_storecard.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.storeCard is not None
    assert pass1.passInformation.__class__ == passes.StoreCard
    assert pass1.nfc is None
    print(pass1.model_dump(exclude_none=True))


def test_load_storecard_nfc():
    buf = open(common.jsons / "storecard_with_nfc.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.storeCard is not None
    assert pass1.passInformation.__class__ == passes.StoreCard

    assert pass1.nfc is not None
    print(pass1.model_dump(exclude_none=True))


def test_load_minimal_generic_pass():
    buf = open(common.jsons / "minimal_generic_pass.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.generic is not None
    assert pass1.passInformation.__class__ == passes.Generic
    json_ = pass1.model_dump(exclude_none=True)
    assert json_


def test_load_generic_pass():
    buf = open(common.jsons / "generic_pass.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.generic is not None
    assert pass1.passInformation.__class__ == passes.Generic
    json_ = pass1.model_dump(exclude_none=True)
    assert json_


def test_load_boarding_pass():
    buf = open(common.jsons / "boarding_pass.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.boardingPass is not None
    assert pass1.passInformation.__class__ == passes.BoardingPass
    json_ = pass1.model_dump(exclude_none=True)
    assert json_


def test_load_event_pass():
    buf = open(common.jsons / "event_ticket.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.eventTicket is not None
    assert pass1.passInformation.__class__ == passes.EventTicket
    json_ = pass1.model_dump(exclude_none=True)
    assert json_


def test_load_coupon():
    buf = open(common.jsons / "coupon.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    assert pass1.coupon is not None
    assert pass1.passInformation.__class__ == passes.Coupon
    json_ = pass1.model_dump(exclude_none=True)
    assert json_


def test_basic_pass():
    pkpass = create_shell_pass()
    passobject = pkpass.pass_object
    assert passobject.formatVersion == 1
    assert passobject.barcodes[0].format == BarcodeFormat.CODE128
    # barcode is a legacy field, it should be the same as the first barcode, but in the legacy format
    # if the barcode format is not in the legacy list, it should be PDF417
    assert passobject.barcode.format == BarcodeFormat.PDF417
    assert len(pkpass.files) == 0

    passfile_json = passobject.model_dump(exclude_none=True)
    assert passfile_json is not None
    assert passfile_json["suppressStripShine"] is False
    assert passfile_json["formatVersion"] == 1
    assert passfile_json["passTypeIdentifier"] == common.PASS_TYPE_IDENTIFIER
    assert passfile_json["serialNumber"] == "1234567"
    assert passfile_json["teamIdentifier"] == "Team Identifier"
    assert passfile_json["organizationName"] == "Org Name"
    assert passfile_json["description"] == "A Sample Pass"


def test_manifest_creation():
    passfile = create_shell_pass()
    manifest_json = passfile._createManifest()
    manifest = json.loads(manifest_json)
    assert "pass.json" in manifest


def test_header_fields():
    passobject = create_shell_pass().pass_object
    passobject.passInformation.addHeaderField("header", "VIP Store Card", "Famous Inc.")
    pass_json = passobject.model_dump(exclude_none=True)
    assert pass_json["storeCard"]["headerFields"][0]["key"] == "header"
    assert pass_json["storeCard"]["headerFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["headerFields"][0]["label"] == "Famous Inc."


def test_secondary_fields():
    passobject = create_shell_pass().pass_object
    passobject.passInformation.addSecondaryField(
        "secondary", "VIP Store Card", "Famous Inc."
    )
    pass_json = passobject.model_dump()
    assert pass_json["storeCard"]["secondaryFields"][0]["key"] == "secondary"
    assert pass_json["storeCard"]["secondaryFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["secondaryFields"][0]["label"] == "Famous Inc."


def test_back_fields():
    passobject = create_shell_pass().pass_object
    passobject.passInformation.addBackField("back1", "VIP Store Card", "Famous Inc.")
    pass_json = passobject.model_dump()
    assert pass_json["storeCard"]["backFields"][0]["key"] == "back1"
    assert pass_json["storeCard"]["backFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["backFields"][0]["label"] == "Famous Inc."


def test_auxiliary_fields():
    passobject = create_shell_pass().pass_object
    passobject.passInformation.addAuxiliaryField("aux1", "VIP Store Card", "Famous Inc.")
    pass_json = passobject.model_dump()
    assert pass_json["storeCard"]["auxiliaryFields"][0]["key"] == "aux1"
    assert pass_json["storeCard"]["auxiliaryFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["auxiliaryFields"][0]["label"] == "Famous Inc."


def test_code128_pass():
    """
    This test is to create a pass with a new code128 format,
    freezes it to json, then reparses it and validates it defaults
    the legacy barcode correctly
    """
    passobject = create_shell_pass(barcodeFormat=BarcodeFormat.CODE128).pass_object
    assert passobject.barcode.format == BarcodeFormat.PDF417
    jsonData = passobject.model_dump_json()
    thawedJson = json.loads(jsonData)

    # the legacy barcode field should be converted to PDF417 because CODE128 is not
    # in the legacy barcode list
    assert thawedJson["barcode"]["format"] == BarcodeFormat.PDF417.value
    assert thawedJson["barcodes"][0]["format"] == BarcodeFormat.CODE128.value


def test_pdf_417_pass():
    """
    This test is to create a pass with a barcode that is valid
    in both past and present versions of IOS
    """
    passobject = create_shell_pass(BarcodeFormat.PDF417).pass_object
    jsonData = passobject.model_dump_json()
    thawedJson = json.loads(jsonData)
    assert thawedJson["barcode"]["format"] == BarcodeFormat.PDF417.value
    assert thawedJson["barcodes"][0]["format"] == BarcodeFormat.PDF417.value


def test_files():
    passfile = create_shell_pass()
    passfile.addFile("icon.png", open(common.resources / "white_square.png", "rb"))
    assert len(passfile.files) == 1
    assert "icon.png" in passfile.files

    manifest_json = passfile._createManifest()
    manifest = json.loads(manifest_json)
    assert "170eed23019542b0a2890a0bf753effea0db181a" == manifest["icon.png"]

    passfile.addFile("logo.png", open(common.resources / "white_square.png", "rb"))
    assert len(passfile.files) == 2
    assert "logo.png" in passfile.files

    manifest_json = passfile._createManifest()
    manifest = json.loads(manifest_json)
    assert "170eed23019542b0a2890a0bf753effea0db181a" == manifest["logo.png"]
