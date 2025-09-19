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

PLUGINS = PassDataAcquisition | PassRegistration | Logging | DynamicSettings


def add_plugin(
    name: str,
    plugin: PassDataAcquisition | PassRegistration | Logging | DynamicSettings,
) -> None:

    if not isinstance(plugin, _PLUGIN_CLASS_NAMES[name]):
        raise TypeError(f"{plugin} not implements {name}")
    if name not in _PLUGIN_REGISTRY:
        _PLUGIN_REGISTRY.setdefault(name, [])
        _PLUGIN_REGISTRY[name].append(plugin)


def remove_plugins(*plugins: PLUGINS) -> None:
    """
    Remove plugins from the registry. Not performant, but it is not called often.
    """
    for plugin in plugins:
        for name, plugin_list in list(_PLUGIN_REGISTRY.items()):
            if plugin in plugin_list:
                plugin_list.remove(plugin)
                if not plugin_list:  # Clean up empty lists
                    del _PLUGIN_REGISTRY[name]
                break


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


def get_dynamic_settings_handlers() -> list[DynamicSettings]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    # allow multiple entries by searching for the prefix
    plugins = [
        ep.load() for ep in eps if ep.name.startswith("DynamicSettings")
    ] + _PLUGIN_REGISTRY.get("DynamicSettings", [])

    # for now we only support one dynamic settings handler
    # for handling multiple handlers we need to define a strategy
    if len(plugins) > 1:
        raise ValueError("multiple DynamicSettings plugins found, only one is allowed")
    for plugin in plugins:
        if not isinstance(plugin, DynamicSettings):
            raise ValueError(f"{plugin} not implements DynamicSettings")
    return [plugin() for plugin in plugins]


def get_dynamic_settings_handler() -> DynamicSettings | None:
    """
    Returns the first dynamic settings handler or None if no handler is found.
    """
    handlers = get_dynamic_settings_handlers()
    if handlers:
        return handlers[0]
    return None
