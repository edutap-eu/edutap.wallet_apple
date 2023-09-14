import os
from pathlib import Path
from edutap.wallet_apple import models

cwd = Path(__file__).parent
data = cwd / 'data'

def test_model():
    pass1 = models.PassInformation(
        headerFields=[
            models.Field(key='header1', value='header1', label='header1'),
        ]
    )
    
    print(pass1.model_dump(exclude_none=True))
    
def test_load_boarding_pass():
    buf = open(data / 'minimal_pass.json', 'r').read()
    pass1 = models.Pass.parse_raw(buf)
    
    assert pass1.storeCard is not None
    print(pass1.model_dump(exclude_none=True))