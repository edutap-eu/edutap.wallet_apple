from .protocols import PassDataAcquisition
from .protocols import PassRegistration
from importlib.metadata import entry_points
from typing import Iterable


def get_pass_registrations() -> Iterable[PassRegistration]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    return [ep.load() for ep in eps if ep.name == "PassRegistration"]


def get_pass_data_acquisitions() -> Iterable[PassDataAcquisition]:
    eps = entry_points(group="edutap.wallet_apple.plugins")
    return [ep.load() for ep in eps if ep.name == "PassDataAcquisition"]
