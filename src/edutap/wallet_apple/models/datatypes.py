from pydantic import BaseModel


class Beacon(BaseModel):
    """
    An object that represents the identifier of a Bluetooth Low Energy beacon the system uses to show a relevant pass.

    see: https://developer.apple.com/documentation/walletpasses/pass/beacons-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

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


class NFC(BaseModel):
    """
    An object that represents the near-field communication (NFC) payload the device passes to an Apple Pay terminal.

    see: https://developer.apple.com/documentation/walletpasses/pass/nfc-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    encryptionPublicKey: str
    """
    Required.
    The public encryption key the Value Added Services protocol uses.
    Use a Base64-encoded X.509 SubjectPublicKeyInfo structure that contains an ECDH public key for group P256.
    """

    message: str
    """
    Required.
    The payload the device transmits to the Apple Pay terminal.
    The size needs to be no more than 64 bytes. The system truncates messages longer than 64 bytes.
    """

    requiresAuthentication: bool = False
    """
    Optional.
    A Boolean value that indicates whether the NFC pass requires authentication.
    The default value is false.
    A value of true requires the user to authenticate for each use of the NFC pass.

    This key is valid in iOS 13.1 and later.
    Set sharingProhibited to true to prevent users from sharing passes with older iOS versions and bypassing the authentication requirement.
    """
