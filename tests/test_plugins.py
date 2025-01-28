def test_get_pass_registrations(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_pass_registrations
    from edutap.wallet_apple.protocols import PassRegistration

    plugins = get_pass_registrations()
    assert len(plugins) == 1
    assert isinstance(plugins[0], PassRegistration)


def test_get_pass_data_acquisitions(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_pass_data_acquisitions
    from edutap.wallet_apple.protocols import PassDataAcquisition

    plugins = get_pass_data_acquisitions()
    assert len(plugins) == 1
    assert isinstance(plugins[0], PassDataAcquisition)
