import json
import os
from pathlib import Path
from edutap.wallet_apple import models
from common import *


def test_model():
    pass1 = models.PassInformation(
        headerFields=[
            models.Field(key='header1', value='header1', label='header1'),
        ]
    )
    
    print(pass1.model_dump(exclude_none=True))
    
    
def test_load_minimal_storecard():
    buf = open(jsons /'minimal_storecard.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.storeCard is not None
    assert pass1.passInformation.__class__ == models.StoreCard
    assert pass1.nfc is None
    print(pass1.model_dump(exclude_none=True))
    
   
def test_load_storecard_nfc():
    buf = open(jsons /'storecard_with_nfc.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.storeCard is not None
    assert pass1.passInformation.__class__ == models.StoreCard
    
    assert pass1.nfc is not None
    print(pass1.model_dump(exclude_none=True))
  
   
def test_load_minimal_generic_pass():
    buf = open(jsons / 'minimal_generic_pass.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.generic is not None
    assert pass1.passInformation.__class__ == models.Generic
    json_ = pass1.model_dump(exclude_none=True)
    
    
def test_load_generic_pass():
    buf = open(jsons / 'generic_pass.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.generic is not None
    assert pass1.passInformation.__class__ == models.Generic
    json_ = pass1.model_dump(exclude_none=True)


def test_load_boarding_pass():
    buf = open(jsons / 'boarding_pass.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.boardingPass is not None
    assert pass1.passInformation.__class__ == models.BoardingPass
    json_ = pass1.model_dump(exclude_none=True)


def test_load_event_pass():
    buf = open(jsons / 'event_ticket.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.eventTicket is not None
    assert pass1.passInformation.__class__ == models.EventTicket
    json_ = pass1.model_dump(exclude_none=True)


def test_load_coupon():
    buf = open(jsons / 'coupon.json', 'r').read()
    pass1 = models.Pass.model_validate_json(buf)
    
    assert pass1.coupon is not None
    assert pass1.passInformation.__class__ == models.Coupon
    json_ = pass1.model_dump(exclude_none=True)


from common import create_shell_pass

def test_basic_pass():
    passfile = create_shell_pass()
    assert passfile.formatVersion == 1
    assert passfile.barcode.format == BarcodeFormat.CODE128
    assert len(passfile.files) == 0

    passfile_json = passfile.model_dump(exclude_none=True)
    assert passfile_json is not None
    assert passfile_json['suppressStripShine'] == False
    assert passfile_json['formatVersion'] == 1
    assert passfile_json['passTypeIdentifier'] == 'Pass Type ID'
    assert passfile_json['serialNumber'] == '1234567'
    assert passfile_json['teamIdentifier'] == 'Team Identifier'
    assert passfile_json['organizationName'] == 'Org Name'
    assert passfile_json['description'] == 'A Sample Pass'


def test_manifest_creation():
    passfile = create_shell_pass()
    manifest_json = passfile._createManifest()
    manifest = json.loads(manifest_json)
    assert "pass.json" in manifest
    
    
def test_header_fields():
    passfile = create_shell_pass()
    passfile.passInformation.addHeaderField("header", "VIP Store Card", "Famous Inc.")
    pass_json = passfile.model_dump(exclude_none=True)
    assert pass_json["storeCard"]["headerFields"][0]["key"] == "header"
    assert pass_json["storeCard"]["headerFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["headerFields"][0]["label"] == "Famous Inc."


def test_secondary_fields():
    passfile = create_shell_pass()
    passfile.passInformation.addSecondaryField(
        "secondary", "VIP Store Card", "Famous Inc."
    )
    pass_json = passfile.model_dump()
    assert pass_json["storeCard"]["secondaryFields"][0]["key"] == "secondary"
    assert pass_json["storeCard"]["secondaryFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["secondaryFields"][0]["label"] == "Famous Inc."


def test_back_fields():
    passfile = create_shell_pass()
    passfile.passInformation.addBackField("back1", "VIP Store Card", "Famous Inc.")
    pass_json = passfile.model_dump()
    assert pass_json["storeCard"]["backFields"][0]["key"] == "back1"
    assert pass_json["storeCard"]["backFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["backFields"][0]["label"] == "Famous Inc."


def test_auxiliary_fields():
    passfile = create_shell_pass()
    passfile.passInformation.addAuxiliaryField("aux1", "VIP Store Card", "Famous Inc.")
    pass_json = passfile.model_dump()
    assert pass_json["storeCard"]["auxiliaryFields"][0]["key"] == "aux1"
    assert pass_json["storeCard"]["auxiliaryFields"][0]["value"] == "VIP Store Card"
    assert pass_json["storeCard"]["auxiliaryFields"][0]["label"] == "Famous Inc."


def test_code128_pass():
    """
    This test is to create a pass with a new code128 format,
    freezes it to json, then reparses it and validates it defaults
    the legacy barcode correctly
    """
    passfile = create_shell_pass(barcodeFormat=BarcodeFormat.CODE128)
    assert passfile.barcode.format == BarcodeFormat.PDF417
    jsonData = passfile.model_dump_json()
    thawedJson = json.loads(jsonData)
    
    # the legacy barcode field should be converted to PDF417 because CODE128 is not 
    # in the legacy barcode list
    assert thawedJson["barcode"]["format"] == BarcodeFormat.PDF417.value
    assert thawedJson["barcodes"][0]["format"] == BarcodeFormat.CODE128.value

