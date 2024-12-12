from .protocols import PassDataAcquisition
from .protocols import PassRegistration
from importlib.metadata import entry_points
from typing import Iterable


def get_pass_registrations() -> Iterable[PassRegistration]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    plugins = [ep.load() for ep in eps if ep.name == "PassRegistration"]
    for plugin in plugins:
        if not isinstance(plugin, PassRegistration):
            raise ValueError(f"{plugin} not implements PassRegistration")
    return [plugin() for plugin in plugins]


def get_pass_data_acquisitions() -> Iterable[PassDataAcquisition]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    plugins = [ep.load() for ep in eps if ep.name == "PassDataAcquisition"]
    for plugin in plugins:
        if not isinstance(plugin, PassDataAcquisition):
            raise ValueError(f"{plugin} not implements PassDataAcquisition")
    return [plugin() for plugin in plugins]
