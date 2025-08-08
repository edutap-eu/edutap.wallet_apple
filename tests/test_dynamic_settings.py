import pytest


class TestDynamicSettings:
    async def get_fernet_key(self, pass_type_identifier: str) -> bytes:
        """
        returns a fernet key. Is used by api.create_auth_token() and api.extract_auth_token()
        """

        return b'1234'

    async def get_private_key(self, pass_type_identifier: str) -> bytes:
        """
        returns a private key depending on a pass type identifier
        """
        return b'12345'
    async def get_pass_certificate(self, pass_type_identifier: str) -> bytes:
        """
        returns a private key depending on a pass type identifier
        """
        return b'123456'


    
    
@pytest.fixture
def dynamic_settings():
    """registers test plugin for dynamic settings"""


def test_dynamic_settings_plugin(dynamic_settings):
    ...