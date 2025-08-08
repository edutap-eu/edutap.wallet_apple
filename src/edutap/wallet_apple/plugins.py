from .protocols import DynamicSettings
from .protocols import Logging
from .protocols import PassDataAcquisition
from .protocols import PassRegistration
from importlib.metadata import entry_points


_PLUGIN_CLASS_NAMES = {
    "PassDataAcquisition": PassDataAcquisition,
    "PassRegistration": PassRegistration,
    "Logging": Logging,
    "DynamicSettings": DynamicSettings,
}
_PLUGIN_REGISTRY: dict[
    str, list[PassDataAcquisition | PassRegistration | Logging | DynamicSettings]
] = {}


def add_plugin(
    name: str,
    plugin: PassDataAcquisition | PassRegistration | Logging | DynamicSettings,
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
    if not plugins:
        raise NotImplementedError("No pass registration plug-in found")
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
    if not plugins:
        raise NotImplementedError("No pass data acquisition plug-in found")
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
    # if not plugins:
    #     raise NotImplementedError("No logging plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, Logging):
            raise ValueError(f"{plugin} not implements Logging")
    return [plugin() for plugin in plugins]


def get_dynamic_settings_handlers() -> list[Logging]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # allow multiple entries by searching for the prefix
    plugins = [
        ep.load() for ep in eps if ep.name.startswith("DynamicSettings")
    ] + _PLUGIN_REGISTRY.get("DynamicSettings", [])
    # if not plugins:
    #     raise NotImplementedError("No logging plug-in found")
    for plugin in plugins:
        if not isinstance(plugin, DynamicSettings):
            raise ValueError(f"{plugin} not implements DynamicSettings")
    return [plugin() for plugin in plugins]
