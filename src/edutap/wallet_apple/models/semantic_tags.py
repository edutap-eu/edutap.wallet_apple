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


SemanticTagType: Literal[
    "additionalTicketAttributes",  # localizable string  # Additional ticket attributes that other tags or keys in the pass don’t include. Use this key for any type of event ticket.
    "admissionLevel",  # localizable string  # The level of admission the ticket provides, such as general admission, VIP, and so forth. Use this key for any type of event ticket.
    "admissionLevelAbbreviation",  # localizable string  # An abbreviation of the level of admission the ticket provides, such as GA or VIP. Use this key for any type of event ticket.
    "airlineCode",  # localizable string  # The IATA airline code, such as EX for flightCode EX123. Use this key only for airline boarding passes.
    "albumIDs",  # [localizable string]  # An array of the Apple Music persistent ID for each album corresponding to the event, in decreasing order of significance. Use this key for any type of event ticket.  #     "artistIDs",  # [localizable string]  # An array of the Apple Music persistent ID for each artist performing at the event, in decreasing order of significance. Use this key for any type of event ticket.
    "attendeeName",  # localizable string  # The name of the person the ticket grants admission to. Use this key for any type of event ticket.
    "awayTeamAbbreviation",  # ",  # localizable string  # The unique abbreviation of the away team’s name. Use this key only for a sports event ticket.
    "awayTeamLocation",  # localizable string  # The home location of the away team. Use this key only for a sports event ticket.
    "awayTeamName",  # localizable string  # The name of the away team. Use this key only for a sports event ticket.
    "balance",  # SemanticTagType.CurrencyAmount  # The current balance redeemable with the pass. Use this key only for a store card pass.
    "boardingGroup",  # localizable string  # A group number for boarding. Use this key for any type of boarding pass.
    "boardingSequenceNumber",  # localizable string  # A sequence number for boarding. Use this key for any type of boarding pass.
    "carNumber",  # localizable string  # The number of the passenger car. A train car is also called a carriage, wagon, coach, or bogie in some countries. Use this key only for a train or other rail boarding pass.
    "confirmationNumber",  # localizable string  # A booking or reservation confirmation number. Use this key for any type of boarding pass.
    "currentArrivalDate",  # ISO 8601 date as string  # The updated date and time of arrival, if different from the originally scheduled date and time. Use this key for any type of boarding pass.
    "currentBoardingDate",  # ISO 8601 date as string  # The updated date and time of boarding, if different from the originally scheduled date and time. Use this key for any type of boarding pass.
    "currentDepartureDate",  # ISO 8601 date as string  # The updated departure date and time, if different from the originally scheduled date and time. Use this key for any type of boarding pass.
    "departureAirportCode",  # localizable string  # The IATA airport code for the departure airport, such as MPM or LHR. Use this key only for airline boarding passes.
    "departureAirportName",  # localizable string  # The full name of the departure airport, such as Maputo International Airport. Use this key only for airline boarding passes.
    "departureGate",  # localizable string  # The gate number or letters of the departure gate, such as 1A. Don’t include the word gate.
    "departureLocation",  # SemanticTagType.Location  # An object that represents the geographic coordinates of the transit departure location, suitable for display on a map. If possible, use precise locations, which are more useful to travelers; for example, the specific location of an airport gate. Use this key for any type of boarding pass.
    "departureLocationDescription",  # localizable string  # A brief description of the departure location. For example, for a flight departing from an airport that has a code of LHR, an appropriate description might be London, Heathrow. Use this key for any type of boarding pass.
    "departurePlatform",  # localizable string  # The name of the departure platform, such as A. Don’t include the word platform. Use this key only for a train or other rail boarding pass.
    "departureStationName",  # localizable string  # The name of the departure station, such as 1st Street Station. Use this key only for a train or other rail boarding pass.
    "departureTerminal",  # localizable string  # The name or letter of the departure terminal, such as A. Don’t include the word terminal. Use this key only for airline boarding passes.
    "destinationAirportCode",  # localizable string  # The IATA airport code for the destination airport, such as MPM or LHR. Use this key only for airline boarding passes.
    "destinationAirportName",  # localizable string  # The full name of the destination airport, such as London Heathrow. Use this key only for airline boarding passes.
    "destinationGate",  # localizable string  # The gate number or letter of the destination gate, such as 1A. Don’t include the word gate. Use this key only for airline boarding passes.
    "destinationLocation",  # SemanticTagType.Location  # An object that represents the geographic coordinates of the transit departure location, suitable for display on a map. Use this key for any type of boarding pass.
    "destinationLocationDescription",  # localizable string  # A brief description of the destination location. For example, for a flight arriving at an airport that has a code of MPM, Maputo might be an appropriate description. Use this key for any type of boarding pass.
    "destinationPlatform",  # localizable string  # The name of the destination platform, such as A. Don’t include the word platform. Use this key only for a train or other rail boarding pass.
    "destinationStationName",  # localizable string  # The name of the destination station, such as 1st Street Station. Use this key only for a train or other rail boarding pass.
    "destinationTerminal",  # localizable string  # The terminal name or letter of the destination terminal, such as A. Don’t include the word terminal. Use this key only for airline boarding passes.
    "duration",  # number  # The duration of the event or transit journey, in seconds. Use this key for any type of boarding pass and any type of event ticket.
    "entranceDescription",  # localizable string  # The long description of the entrance information. Use this key for any type of event ticket.
    "eventEndDate",  # ISO 8601 date as string  # The date and time the event ends. Use this key for any type of event ticket.
    "eventName",  # localizable string  # The full name of the event, such as the title of a movie. Use this key for any type of event ticket.
    "eventStartDate",  # ISO 8601 date as string  # The date and time the event starts. Use this key for any type of event ticket.
    "eventStartDateInfo",  # SemanticTagType.EventDateInfo  # An object that provides information for the date and time the event starts. Use this key for any type of event ticket.
    "eventType",  # EventType  # The type of event. Use this key for any type of event ticket.
    "flightCode",  # localizable string  # The IATA flight code, such as EX123. Use this key only for airline boarding passes.
    "flightNumber",  # number  # The numeric portion of the IATA flight code, such as 123 for flightCode EX123. Use this key only for airline boarding passes.
    "genre",  # localizable string  # The genre of the performance, such as classical. Use this key for any type of event ticket.
    "homeTeamAbbreviation",  # localizable string  # The unique abbreviation of the home team’s name. Use this key only for a sports event ticket.
    "homeTeamLocation",  # localizable string  # The home location of the home team. Use this key only for a sports event ticket.
    "homeTeamName",  # localizable string  # The name of the home team. Use this key only for a sports event ticket.
    "leagueAbbreviation",  # localizable string  # The abbreviated league name for a sports event. Use this key only for a sports event ticket.
    "leagueName",  # localizable string  # The unabbreviated league name for a sports event. Use this key only for a sports event ticket.
    "membershipProgramName",  # localizable string  # The name of a frequent flyer or loyalty program. Use this key for any type of boarding pass.
    "membershipProgramNumber",  # localizable string  # The ticketed passenger’s frequent flyer or loyalty number. Use this key for any type of boarding pass.
    "originalArrivalDate",  # ISO 8601 date as string  # The originally scheduled date and time of arrival. Use this key for any type of boarding pass.
    "originalBoardingDate",  # ISO 8601 date as string  # The originally scheduled date and time of boarding. Use this key for any type of boarding pass.
    "originalDepartureDate",  # ISO 8601 date as string  # The originally scheduled date and time of departure. Use this key for any type of boarding pass.
    "passengerName",  # SemanticTagType.PersonNameComponents  # An object that represents the name of the passenger. Use this key for any type of boarding pass.
    "performerNames",  # [localizable string]  # An array of the full names of the performers and opening acts at the event, in decreasing order of significance. Use this key for any type of event ticket.
    "playlistIDs",  # [localizable string]  # An array of the Apple Music persistent ID for each playlist corresponding to the event, in decreasing order of significance. Use this key for any type of event ticket.
    "priorityStatus",  # localizable string  # The priority status the ticketed passenger holds, such as Gold or Silver. Use this key for any type of boarding pass.
    "seats",  # [SemanticTagType.Seat]  # An array of objects that represent the details for each seat at an event or on a transit journey. Use this key for any type of boarding pass or event ticket.
    "securityScreening",  # localizable string  # The type of security screening for the ticketed passenger, such as Priority. Use this key for any type of boarding pass.
    "silenceRequested",  # boolean  # A Boolean value that determines whether the person’s device remains silent during an event or transit journey. The system may override the key and determine the length of the period of silence. Use this key for any type of boarding pass or event ticket.
    "sportName",  # localizable string  # The commonly used name of the sport. Use this key only for a sports event ticket.
    "tailgatingAllowed",  # boolean  # A Boolean value that indicates whether tailgating is allowed at the event. Use this key for any type of event ticket.
    "totalPrice",  # SemanticTagType.CurrencyAmount  # The total price for the pass. Use this key for any pass type.
    "transitProvider",  # localizable string  # The name of the transit company. Use this key for any type of boarding pass.
    "transitStatus",  # localizable string  # A brief description of the current boarding status for the vessel, such as On Time or Delayed. For delayed status, provide currentBoardingDate, currentDepartureDate, and currentArrivalDate where available. Use this key for any type of boarding pass.
    "transitStatusReason",  # localizable string  # A brief description that explains the reason for the current transitStatus, such as Thunderstorms. Use this key for any type of boarding pass.
    "vehicleName",  # localizable string  # The name of the vehicle to board, such as the name of a boat. Use this key for any type of boarding pass.
    "vehicleNumber",  # localizable string  # The identifier of the vehicle to board, such as the aircraft registration number or train number. Use this key for any type of boarding pass.
    "vehicleType",  # localizable string  # A brief description of the type of vehicle to board, such as the model and manufacturer of a plane or the class of a boat. Use this key for any type of boarding pass.
    "venueBoxOfficeOpenDate",  # ISO 8601 date as string  # The date when the box office opens. Use this key for any type of event ticket.
    "venueCloseDate",  # ISO 8601 date as string  # The date when the venue closes. Use this key for any type of event ticket.
    "venueDoorsOpenDate",  # ISO 8601 date as string  # The date the doors to the venue open. Use this key for any type of event ticket.
    "venueEntrance",  # localizable string  # The full name of the entrance, such as Gate A, to use to gain access to the ticketed event. Use this key for any type of event ticket.
    "venueEntranceDoor",  # localizable string  # The venue entrance door. Use this key for any type of event ticket.
    "venueEntranceGate",  # localizable string  # The venue entrance gate. Use this key for any type of event ticket.
    "venueEntrancePortal",  # localizable string  # The venue entrance portal. Use this key for any type of event ticket.
    "venueFanZoneOpenDate",  # ISO 8601 date as string  # The date the fan zone opens. Use this key for any type of event ticket.
    "venueGatesOpenDate",  # ISO 8601 date as string  # The date the gates to the venue open. Use this key for any type of event ticket.
    "venueLocation",  # SemanticTagType.Location  # An object that represents the geographic coordinates of the venue. Use this key for any type of event ticket.
    "venueName",  # localizable string  # The full name of the venue. Use this key for any type of event ticket.
    "venueOpenDate",  # ISO 8601 date as string  # The date when the venue opens. Use this if none of the more specific venue open tags apply. Use this key for any type of event ticket.
    "venueParkingLotsOpenDate",  # ISO 8601 date as string  # The date the parking lots open. Use this key for any type of event ticket.
    "venuePhoneNumber",  # localizable string  # The phone number for inquiries about the venue’s ticketed event. Use this key for any type of event ticket.
    "venueRegionName",  # localizable string  # The name of the city or hosting region of the venue. Use this key for any type of event ticket.
    "venueRoom",  # localizable string  # The full name of the room where the ticketed event is to take place. Use this key for any type of event ticket.
    "wifiAccess",  # [SemanticTagType.WifiNetwork]  # An array of objects that represent the Wi-Fi networks associated with the event; for example, the network name and password associated with a developer conference. Use this key for any type of pass.
]
