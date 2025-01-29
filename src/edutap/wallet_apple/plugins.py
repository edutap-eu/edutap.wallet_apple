from .protocols import Logging
from .protocols import PassDataAcquisition
from .protocols import PassRegistration
from importlib.metadata import entry_points


def get_pass_registrations() -> list[PassRegistration]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # allow multiple entries by searching for the prefix
    plugins = [ep.load() for ep in eps if ep.name.startswith("PassRegistration")]
    if not plugins:
        raise NotImplementedError("No pass registration plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, PassRegistration):
            raise ValueError(f"{plugin} not implements PassRegistration")
    return [plugin() for plugin in plugins]


def get_pass_data_acquisitions() -> list[PassDataAcquisition]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # here we only allow one entry, so we search for the exact name
    plugins = [ep.load() for ep in eps if ep.name == "PassDataAcquisition"]
    if not plugins:
        raise NotImplementedError("No pass data acquisition plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, PassDataAcquisition):
            raise ValueError(f"{plugin} not implements PassDataAcquisition")
    return [plugin() for plugin in plugins]


def get_logging_handlers() -> list[Logging]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # allow multiple entries by searching for the prefix
    plugins = [ep.load() for ep in eps if ep.name.startswith("Logging")]
    # if not plugins:
    #     raise NotImplementedError("No logging plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, Logging):
            raise ValueError(f"{plugin} not implements Logging")
    return [plugin() for plugin in plugins]
