from pydantic import BaseModel
from typing import Literal


# Attribute order as in Apple's documentation to make future changes easier!
# last checked: 2025-05-16

EventType: Literal[
    "PKEventTypeGeneric",
    "PKEventTypeLivePerformance",
    "PKEventTypeMovie",
    "PKEventTypeSports",
    "PKEventTypeConference",
    "PKEventTypeConvention",
    "PKEventTypeWorkshop",
    "PKEventTypeSocialGathering",
]


class CurrencyAmount(BaseModel):
    """
    An object that represents an amount of money and type of currency.

    see: https://developer.apple.com/documentation/walletpasses/semantictagtype/currencyamount-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    amount: str
    """
    Required.

    The amount of money.
    """

    currencyCode: str
    """
    Required. ISO 4217 currency code as a string

    The currency code for amount.
    """


class EventDateInfo(BaseModel):
    """
    An object that represents a date for an event.

    see: https://developer.apple.com/documentation/walletpasses/semantictagtype/eventdateinfo-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    date: str | None = None
    """
    Required. ISO 8601 date as string
    The date.
    """

    ignoreTimeComponents: bool | None = None
    """
    Optional.
    A Boolean value that indicates whether the system ignores the time components of the date.
    """

    timeZone: str | None = None
    """
    Optional. Time zone database identifier as string
    The time zone to display in the date.
    """

    unannounced: bool | None = None
    """
    Optional.
    A Boolean value that indicates whether the date of the event is announced.
    """

    undetermined: bool | None = None
    """
    Optional.
    A Boolean value that indicates whether the date of the event is determined.
    """


class Location(BaseModel):
    """
    An object that represents the coordinates of a location.

    see: https://developer.apple.com/documentation/walletpasses/semantictagtype/location-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    latitude: float
    """
    Required.
    The latitude, in degrees.
    """

    longitude: float
    """
    Required.
    The longitude, in degrees.
    """


class PersonNameComponents(BaseModel):
    """
    An object that represents the parts of a person’s name.
    see: https://developer.apple.com/documentation/walletpasses/semantictagtype/personnamecomponents-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    familyName: str | None = None
    """
    Optional. string
    The person’s family name or last name.
    """

    givenName: str | None = None
    """
    Optional. string
    The person’s given name; also called the forename or first name in some countries.
    """

    middleName: str | None = None
    """
    Optional. string
    The person’s middle name.
    """

    namePrefix: str | None = None
    """
    Optional. string
    The prefix for the person’s name, such as “Dr”.
    """

    nameSuffix: str | None = None
    """
    Optional. string
    The suffix for the person’s name, such as “Junior”.
    """

    nickname: str | None = None
    """
    Optional. string
    The person’s nickname.
    """

    phoneticRepresentation: str | None = None
    """
    Optional. string
    The phonetic representation of the person’s name.
    """


class Seat(BaseModel):
    """
    An object that represents the identification of a seat for a transit journey or an event.

    see: https://developer.apple.com/documentation/walletpasses/semantictagtype/seat-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    seatAisle: str | None = None
    """
    Optional. localizable string
    The aisle that contains the seat.
    """

    seatDescription: str | None = None
    """
    Optional. localizable string
    A description of the seat, such as A flat bed seat.
    """

    seatIdentifier: str | None = None
    """
    Optional. localizable string
    The identifier code for the seat.
    """

    seatLevel: str | None = None
    """
    Optional. localizable string
    The level that contains the seat.
    """

    seatNumber: str | None = None
    """
    Optional. localizable string
    The number of the seat.
    """

    seatRow: str | None = None
    """
    Optional. localizable string
    The row that contains the seat.
    """

    seatSection: str | None = None
    """
    Optional. localizable string
    The section that contains the seat.
    """

    seatSectionColor: str | None = None
    """
    Optional. RGB triple as string
    A color associated with identifying the seat, specified as a CSS-style RGB triple, such as rgb(23, 187, 82).
    """

    seatType: str | None = None
    """
    Optional. localizable string
    The type of seat, such as Reserved seating.
    """


class WifiNetwork(BaseModel):
    """
    An object that contains information required to connect to a WiFi network.

    see: https://developer.apple.com/documentation/walletpasses/semantictagtype/wifinetwork-data.dictionary
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    password: str
    """
    Required.
    The password for the WiFi network.
    """

    ssid: str
    """
    Required.
    The name of the WiFi network.
    """


class SportEventTypeSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for event tickets.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    awayTeamAbbreviation: str | None = None
    """
    Optional. localizable string
    The unique abbreviation of the away team’s name.
    Use this key only for a sports event ticket.
    """

    awayTeamLocation: str | None = None
    """
    Optional.
    localizable string
    The home location of the away team.
    Use this key only for a sports event ticket.
    """

    awayTeamName: str | None = None
    """
    Optional. localizable string
    The name of the away team.
    Use this key only for a sports event ticket.
    """

    homeTeamAbbreviation: str | None = None
    """
    Optional.
    localizable string  # The unique abbreviation of the home team’s name.
    Use this key only for a sports event ticket.
    """

    homeTeamLocation: str | None = None
    """
    Optional.
    localizable string  # The home location of the home team.
    Use this key only for a sports event ticket.
    """

    homeTeamName: str | None = None
    """
    Optional.
    localizable string  # The name of the home team.
    Use this key only for a sports event ticket.
    """

    leagueAbbreviation: str | None = None
    """
    Optional.
    localizable string  # The abbreviated league name for a sports event.
    Use this key only for a sports event ticket.
    """

    leagueName: str | None = None
    """
    Optional.
    localizable string  # The unabbreviated league name for a sports event.
    Use this key only for a sports event ticket.
    """


class EventTicketSemanticTags(SportEventTypeSemanticTags):
    """
    Subclass of SemanticTags. with only the relevant attributes for event tickets.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16
    additionalTicketAttributes: str | None = None
    """
    Optional. localizable string
    Additional ticket attributes that other tags or keys in the pass don’t include.
    Use this key for any type of event ticket.
    """

    admissionLevel: str | None = None
    """
    Optional. localizable string
    The level of admission the ticket provides, such as general admission, VIP, and so forth.
    Use this key for any type of event ticket.
    """

    admissionLevelAbbreviation: str | None = None
    """
    Optional. localizable string
    An abbreviation of the level of admission the ticket provides, such as GA or VIP.
    Use this key for any type of event ticket.
    """

    albumIDs: list[str] | None = None
    """
    Optional. [localizable string]
    An array of the Apple Music persistent ID for each album corresponding to the event, in decreasing order of significance.
    Use this key for any type of event ticket.
    """

    artistIDs: list[str] | None = None
    """
    Optional. [localizable string]
    An array of the Apple Music persistent ID for each artist performing at the event, in decreasing order of significance.
    Use this key for any type of event ticket.
    """

    attendeeName: str | None = None
    """
    Optional. localizable string
    The name of the person the ticket grants admission to.
    Use this key for any type of event ticket.
    """

    # inherits awayTeamAbbreviation
    # inherits awayTeamLocation
    # inherits awayTeamName

    duration: int | None = None
    """
    Optional. number
    The duration of the event or transit journey, in seconds.
    Use this key for any type of boarding pass and any type of event ticket.
    """

    entranceDescription: str | None = None
    """
    Optional. localizable string
    The long description of the entrance information.
    Use this key for any type of event ticket.
    """

    eventEndDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The date and time the event ends.
    Use this key for any type of event ticket.
    """

    eventName: str | None = None
    """
    Optional. localizable string
    The full name of the event, such as the title of a movie.
    Use this key for any type of event ticket.
    """

    eventStartDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The date and time the event starts.
    Use this key for any type of event ticket.
    """

    eventStartDateInfo: EventDateInfo | None = None
    """
    Optional. SemanticTagType.EventDateInfo
    An object that provides information for the date and time the event starts.
    Use this key for any type of event ticket.
    """

    eventType: (
        Literal[
            "PKEventTypeGeneric",
            "PKEventTypeLivePerformance",
            "PKEventTypeMovie",
            "PKEventTypeSports",
            "PKEventTypeConference",
            "PKEventTypeConvention",
            "PKEventTypeWorkshop",
            "PKEventTypeSocialGathering",
        ]
        | None
    ) = None
    """
    Optional. EventType
    The type of event.
    Use this key for any type of event ticket.
    """

    genre: str | None = None
    """
    Optional.
    localizable string  # The genre of the performance, such as classical.
    Use this key for any type of event ticket.
    """


class PKTransitTypeAirSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for Airline Boarding Passes.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    airlineCode: str | None = None
    """
    Optional. localizable string
    The IATA airline code, such as EX for flightCode EX123.
    Use this key only for airline boarding passes.
    """


class PKTransitTypeBoatSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for Boat Boarding Passes.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16


class PKTransitTypeBusSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for Bus Boarding Passes.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16


class PKTransitTypeGenericSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for Generic Boarding Passes.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16


class PKTransitTypeTrainSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for Train Boarding Passes.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16


class BoardingPassSemanticTags(
    PKTransitTypeAirSemanticTags,
    PKTransitTypeBoatSemanticTags,
    PKTransitTypeBusSemanticTags,
    PKTransitTypeGenericSemanticTags,
    PKTransitTypeTrainSemanticTags,
):
    """
    Subclass of SemanticTags. with only the relevant attributes for boarding passes.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    # inherits airlineCode

    boardingGroup: str | None = None
    """
    Optional. localizable string
    A group number for boarding.
    Use this key for any type of boarding pass.
    """

    boardingSequenceNumber: str | None = None
    """
    Optional. localizable string
    A sequence number for boarding.
    Use this key for any type of boarding pass.
    """

    carNumber: str | None = None
    """
    Optional. localizable string
    The number of the passenger car. A train car is also called a carriage, wagon, coach, or bogie in some countries.
    Use this key only for a train or other rail boarding pass.
    """
    confirmationNumber: str | None = None
    """
    Optional. localizable string
    A booking or reservation confirmation number.
    Use this key for any type of boarding pass.
    """

    currentArrivalDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The updated date and time of arrival, if different from the originally scheduled date and time.
    Use this key for any type of boarding pass.
    """

    currentBoardingDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The updated date and time of boarding, if different from the originally scheduled date and time.
    Use this key for any type of boarding pass.
    """

    currentDepartureDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The updated departure date and time, if different from the originally scheduled date and time.
    Use this key for any type of boarding pass.
    """

    departureAirportCode: str | None = None
    """
    Optional. localizable string
    The IATA airport code for the departure airport, such as MPM or LHR.
    Use this key only for airline boarding passes.
    """

    departureAirportName: str | None = None
    """
    Optional. localizable string
    The full name of the departure airport, such as Maputo International Airport.
    Use this key only for airline boarding passes.
    """

    departureGate: str | None = None
    """
    Optional. localizable string
    The gate number or letters of the departure gate, such as 1A. Don’t include the word gate.
    """

    departureLocation: Location | None = None
    """
    Optional.
    SemanticTagType.Location  # An object that represents the geographic coordinates of the transit departure location, suitable for display on a map. If possible, use precise locations, which are more useful to travelers; for example, the specific location of an airport gate.
    Use this key for any type of boarding pass.
    """

    departureLocationDescription: str | None = None
    """
    Optional.
    localizable string  # A brief description of the departure location. For example, for a flight departing from an airport that has a code of LHR, an appropriate description might be London, Heathrow.
    Use this key for any type of boarding pass.
    """

    departurePlatform: str | None = None
    """
    Optional.
    localizable string  # The name of the departure platform, such as A. Don’t include the word platform.
    Use this key only for a train or other rail boarding pass.
    """

    departureStationName: str | None = None
    """
    Optional.
    localizable string  # The name of the departure station, such as 1st Street Station.
    Use this key only for a train or other rail boarding pass.
    """

    departureTerminal: str | None = None
    """
    Optional.
    localizable string  # The name or letter of the departure terminal, such as A. Don’t include the word terminal.
    Use this key only for airline boarding passes.
    """

    destinationAirportCode: str | None = None
    """
    Optional.
    localizable string  # The IATA airport code for the destination airport, such as MPM or LHR.
    Use this key only for airline boarding passes.
    """

    destinationAirportName: str | None = None
    """
    Optional.
    localizable string  # The full name of the destination airport, such as London Heathrow.
    Use this key only for airline boarding passes.
    """

    destinationGate: str | None = None
    """
    Optional.
    localizable string  # The gate number or letter of the destination gate, such as 1A. Don’t include the word gate.
    Use this key only for airline boarding passes.
    """

    destinationLocation: str | None = None
    """
    Optional.
    SemanticTagType.Location  # An object that represents the geographic coordinates of the transit departure location, suitable for display on a map.
    Use this key for any type of boarding pass.
    """

    destinationLocationDescription: str | None = None
    """
    Optional.
    localizable string  # A brief description of the destination location. For example, for a flight arriving at an airport that has a code of MPM, Maputo might be an appropriate description.
    Use this key for any type of boarding pass.
    """

    destinationPlatform: str | None = None
    """
    Optional.
    localizable string  # The name of the destination platform, such as A. Don’t include the word platform.
    Use this key only for a train or other rail boarding pass.
    """

    destinationStationName: str | None = None
    """
    Optional.
    localizable string  # The name of the destination station, such as 1st Street Station.
    Use this key only for a train or other rail boarding pass.
    """

    destinationTerminal: str | None = None
    """
    Optional.
    localizable string  # The terminal name or letter of the destination terminal, such as A. Don’t include the word terminal.
    Use this key only for airline boarding passes.
    """

    duration: int | None = None
    """
    Optional. number
    The duration of the event or transit journey, in seconds.
    Use this key for any type of boarding pass and any type of event ticket.
    """

    flightCode: str | None = None
    """
    Optional. localizable string
    The IATA flight code, such as EX123.
    Use this key only for airline boarding passes.
    """

    flightNumber: str | None = None
    """
    Optional.
    number  # The numeric portion of the IATA flight code, such as 123 for flightCode EX123.
    Use this key only for airline boarding passes.
    """


class StoreCardSemanticTags(BaseModel):
    """
    Subclass of SemanticTags. with only the relevant attributes for store cards.
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    balance: CurrencyAmount | None = None
    """
    Optional.
    The current balance redeemable with the pass.
    Use this key only for a store card pass.
    """


class SemanticTags(EventTicketSemanticTags, BoardingPassSemanticTags):
    """
    An object that contains machine-readable metadata the system uses to offer a pass and suggest related actions.

    see: https://developer.apple.com/documentation/WalletPasses/SemanticTags
    """

    # Attribute order as in Apple's documentation to make future changes easier!
    # last checked: 2025-05-16

    # inherits additionalTicketAttributes
    # inherits admissionLevel
    # inherits admissionLevelAbbreviation
    # inherits airlineCode
    # inherits albumIDs
    # inherits artistIDs
    # inherits attendeeName
    # inherits awayTeamAbbreviation
    # inherits awayTeamLocation
    # inherits awayTeamName
    # inherits balance
    # inherits boardingGroup
    # inherits boardingSequenceNumber
    # inherits carNumber
    # inherits confirmationNumber
    # inherits currentArrivalDate
    # inherits currentBoardingDate
    # inherits currentDepartureDate
    # inherits departureAirportCode
    # inherits departureAirportName
    # inherits departureGate
    # inherits departureLocation
    # inherits departureLocationDescription
    # inherits departurePlatform
    # inherits departureStationName
    # inherits departureTerminal
    # inherits destinationAirportCode
    # inherits destinationAirportName
    # inherits destinationGate
    # inherits destinationLocation
    # inherits destinationLocationDescription
    # inherits destinationPlatform
    # inherits destinationStationName
    # inherits destinationTerminal
    # inherits duration
    # inherits entranceDescription
    # inherits eventEndDate
    # inherits eventName
    # inherits eventStartDate
    # inherits eventStartDateInfo
    # inherits eventType
    # inherits flightCode
    # inherits flightNumber
    # inherits genre
    # inherits homeTeamAbbreviation
    # inherits homeTeamLocation
    # inherits homeTeamName
    # inherits leagueAbbreviation
    # inherits leagueName

    # inherits membershipProgramName
    # inherits membershipProgramNumber
    # inherits originalArrivalDate
    # inherits originalBoardingDate
    # inherits originalDepartureDate
    # inherits passengerName
    # inherits performerNames

    membershipProgramName: str | None = None
    """
    Optional.
    localizable string  # The name of a frequent flyer or loyalty program.
    Use this key for any type of boarding pass.
    """

    membershipProgramNumber: str | None = None
    """
    Optional.
    localizable string  # The ticketed passenger’s frequent flyer or loyalty number.
    Use this key for any type of boarding pass.
    """

    originalArrivalDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The originally scheduled date and time of arrival.
    Use this key for any type of boarding pass.
    """

    originalBoardingDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The originally scheduled date and time of boarding.
    Use this key for any type of boarding pass.
    """

    originalDepartureDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The originally scheduled date and time of departure.
    Use this key for any type of boarding pass.
    """

    passengerName: str | None = None
    """
    Optional.
    SemanticTagType.PersonNameComponents  # An object that represents the name of the passenger.
    Use this key for any type of boarding pass.
    """

    performerNames: list[str] | None = None
    """
    Optional.
    [localizable string]  # An array of the full names of the performers and opening acts at the event, in decreasing order of significance.
    Use this key for any type of event ticket.
    """

    playlistIDs: str | None = None
    """
    Optional.
    [localizable string]  # An array of the Apple Music persistent ID for each playlist corresponding to the event, in decreasing order of significance.
    Use this key for any type of event ticket.
    """

    priorityStatus: str | None = None
    """
    Optional.
    localizable string  # The priority status the ticketed passenger holds, such as Gold or Silver.
    Use this key for any type of boarding pass.
    """

    seats: list[Seat] | None = None
    """
    Optional. [SemanticTagType.Seat]
    An array of objects that represent the details for each seat at an event or on a transit journey.
    Use this key for any type of boarding pass or event ticket.
    """

    securityScreening: str | None = None
    """
    Optional. localizable string
    The type of security screening for the ticketed passenger, such as Priority.
    Use this key for any type of boarding pass.
    """

    silenceRequested: bool | None = None
    """
    Optional. boolean
    A Boolean value that determines whether the person’s device remains silent during an event or transit journey. The system may override the key and determine the length of the period of silence.
    Use this key for any type of boarding pass or event ticket.
    """

    sportName: str | None = None
    """
    Optional. localizable string
    The commonly used name of the sport.
    Use this key only for a sports event ticket.
    """

    tailgatingAllowed: bool | None = None
    """
    Optional. boolean
    A Boolean value that indicates whether tailgating is allowed at the event.
    Use this key for any type of event ticket.
    """

    totalPrice: CurrencyAmount | None = None
    """
    Optional. SemanticTagType.CurrencyAmount
    The total price for the pass.
    Use this key for any pass type.
    """

    transitProvider: str | None = None
    """
    Optional. localizable string
    The name of the transit company.
    Use this key for any type of boarding pass.
    """

    transitStatus: str | None = None
    """
    Optional. localizable string
    A brief description of the current boarding status for the vessel, such as On Time or Delayed.
    For delayed status, provide currentBoardingDate, currentDepartureDate, and currentArrivalDate where available.
    Use this key for any type of boarding pass.
    """

    transitStatusReason: str | None = None
    """
    Optional. localizable string
    A brief description that explains the reason for the current transitStatus, such as Thunderstorms.
    Use this key for any type of boarding pass.
    """

    vehicleName: str | None = None
    """
    Optional. localizable string
    The name of the vehicle to board, such as the name of a boat.
    Use this key for any type of boarding pass.
    """

    vehicleNumber: str | None = None
    """
    Optional. localizable string
    The identifier of the vehicle to board, such as the aircraft registration number or train number.
    Use this key for any type of boarding pass.
    """

    vehicleType: str | None = None
    """
    Optional. localizable string
    A brief description of the type of vehicle to board, such as the model and manufacturer of a plane or the class of a boat.
    Use this key for any type of boarding pass.
    """

    venueBoxOfficeOpenDate: str | None = None
    """
    Optional. ISO 8601 date as string
    The date when the box office opens.
    Use this key for any type of event ticket.
    """

    venueCloseDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The date when the venue closes.
    Use this key for any type of event ticket.
    """

    venueDoorsOpenDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The date the doors to the venue open.
    Use this key for any type of event ticket.
    """

    venueEntrance: str | None = None
    """
    Optional.
    localizable string  # The full name of the entrance, such as Gate A, to use to gain access to the ticketed event.
    Use this key for any type of event ticket.
    """

    venueEntranceDoor: str | None = None
    """
    Optional.
    localizable string  # The venue entrance door.
    Use this key for any type of event ticket.
    """

    venueEntranceGate: str | None = None
    """
    Optional.
    localizable string  # The venue entrance gate.
    Use this key for any type of event ticket.
    """

    venueEntrancePortal: str | None = None
    """
    Optional.
    localizable string  # The venue entrance portal.
    Use this key for any type of event ticket.
    """

    venueFanZoneOpenDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The date the fan zone opens.
    Use this key for any type of event ticket.
    """

    venueGatesOpenDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The date the gates to the venue open.
    Use this key for any type of event ticket.
    """

    venueLocation: str | None = None
    """
    Optional.
    SemanticTagType.Location  # An object that represents the geographic coordinates of the venue.
    Use this key for any type of event ticket.
    """

    venueName: str | None = None
    """
    Optional.
    localizable string  # The full name of the venue.
    Use this key for any type of event ticket.
    """

    venueOpenDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The date when the venue opens. Use this if none of the more specific venue open tags apply.
    Use this key for any type of event ticket.
    """

    venueParkingLotsOpenDate: str | None = None
    """
    Optional.
    ISO 8601 date as string  # The date the parking lots open.
    Use this key for any type of event ticket.
    """

    venuePhoneNumber: str | None = None
    """
    Optional. localizable string
    The phone number for inquiries about the venue’s ticketed event.
    Use this key for any type of event ticket.
    """

    venueRegionName: str | None = None
    """
    Optional. localizable string
    The name of the city or hosting region of the venue.
    Use this key for any type of event ticket.
    """

    venueRoom: str | None = None
    """
    Optional.  localizable string
    The full name of the room where the ticketed event is to take place.
    Use this key for any type of event ticket.
    """

    wifiAccess: str | None = None
    """
    Optional. [SemanticTagType.WifiNetwork]
    An array of objects that represent the Wi-Fi networks associated with the event; for example, the network name and password associated with a developer conference.
    Use this key for any type of pass.
    """
