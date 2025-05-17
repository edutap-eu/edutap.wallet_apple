from pydantic import BaseModel


class RelevantDate(BaseModel):
    """
    An object that represents a date interval that the system uses to show a relevant pass.

    see: https://developer.apple.com/documentation/walletpasses/pass/relevantdates-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    date: str | None = None
    """
    Optional. ISO 8601 date as string
    The date and time when the pass becomes relevant.
    Wallet automatically calculates a relevancy interval from this date.
    """
    endDate: str | None = None
    """
    Optional. ISO 8601 date as string
    Date and time when the pass becomes irrelevant
    """
    startDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The date and time for the pass relevancy interval to end.
    Required when providing startDate.
    """


class Beacon(BaseModel):
    """
    An object that represents the identifier of a Bluetooth Low Energy beacon the system uses to show a relevant pass.
    see: https://developer.apple.com/documentation/walletpasses/pass/beacons-data.dictionary
    """

    major: int
    """
    Required.
    Major identifier of a Bluetooth Low Energy location beacon.
    """

    minor: int
    """
    Required.
    Minor identifier of a Bluetooth Low Energy location beacon.
    """

    proximityUUID: str
    """
    Required.
    Unique identifier of a Bluetooth Low Energy location beacon.
    """

    relevantText: str | None = None
    """
    Optional.
    The text to display on the lock screen when the pass is relevant.
    For example, a description of a nearby location, such as “Store nearby on 1st and Main”.
    """