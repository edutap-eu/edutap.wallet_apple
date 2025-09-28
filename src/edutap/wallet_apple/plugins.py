from .protocols import Logging
from .protocols import PassDataAcquisition
from .protocols import PassRegistration
from importlib.metadata import entry_points


_PLUGIN_CLASS_NAMES = {
    "PassDataAcquisition": PassDataAcquisition,
    "PassRegistration": PassRegistration,
    "Logging": Logging,
}


_PLUGIN_REGISTRY: dict[str, list[PassDataAcquisition | PassRegistration | Logging]] = {}

PLUGINS = PassDataAcquisition | PassRegistration | Logging


def add_plugin(
    name: str,
    plugin: PassDataAcquisition | PassRegistration | Logging,
) -> None:

    if not isinstance(plugin, _PLUGIN_CLASS_NAMES[name]):
        raise TypeError(f"{plugin} not implements {name}")
    if name not in _PLUGIN_REGISTRY:
        _PLUGIN_REGISTRY.setdefault(name, [])
        _PLUGIN_REGISTRY[name].append(plugin)


def get_pass_registrations() -> list[PassRegistration]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # allow multiple entries by searching for the prefix
    plugins = [
        ep.load() for ep in eps if ep.name.startswith("PassRegistration")
    ] + _PLUGIN_REGISTRY.get("PassRegistration", [])
    for plugin in plugins:
        if not isinstance(plugin, PassRegistration):
            raise ValueError(f"{plugin} not implements PassRegistration")
    return [plugin() for plugin in plugins]


def get_pass_data_acquisitions() -> list[PassDataAcquisition]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # here we only allow one entry, so we search for the exact name
    plugins = [
        ep.load() for ep in eps if ep.name == "PassDataAcquisition"
    ] + _PLUGIN_REGISTRY.get("PassDataAcquisition", [])
    for plugin in plugins:
        if not isinstance(plugin, PassDataAcquisition):
            raise ValueError(f"{plugin} not implements PassDataAcquisition")
    return [plugin() for plugin in plugins]


def get_logging_handlers() -> list[Logging]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # allow multiple entries by searching for the prefix
    plugins = [
        ep.load() for ep in eps if ep.name.startswith("Logging")
    ] + _PLUGIN_REGISTRY.get("Logging", [])
    for plugin in plugins:
        if not isinstance(plugin, Logging):
            raise ValueError(f"{plugin} not implements Logging")
    return [plugin() for plugin in plugins]
