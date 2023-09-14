import os
from pathlib import Path
from edutap.wallet_apple import models

cwd = Path(__file__).parent
data = cwd / 'data'
jsons = data / 'jsons'


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
