import pytest


@pytest.mark.skip(reason="not implemented yet")
def test_get_pass_registrations():
    from edutap.wallet_apple.plugins import get_pass_registrations
    from edutap.wallet_apple.protocols import PassRegistration

    plugins = get_pass_registrations()
    assert len(plugins) == 1
    assert isinstance(plugins[0], PassRegistration)


@pytest.mark.skip(reason="not implemented yet")
def test_get_pass_data_acquisitions():
    from edutap.wallet_apple.plugins import get_pass_data_acquisitions
    from edutap.wallet_apple.protocols import PassDataAcquisition

    plugins = get_pass_data_acquisitions()
    assert len(plugins) == 1
    assert isinstance(plugins[0], PassDataAcquisition)
