from edutap.wallet_apple import api as apple_api
from edutap.wallet_apple.models import datatypes as apple_datatypes
from edutap.wallet_apple.models import passes
from edutap.wallet_apple.models import semantic_tags
from edutap.wallet_apple.models.semantic_tags import EventTicketSemanticTags
from edutap.wallet_apple.models.semantic_tags import Location
from edutap.wallet_apple.models.semantic_tags import Location as SemanticLocation
from pydantic import ValidationError

import json
import pytest


def test_semantic_tags():

    passes.SemanticPassFieldContent(
        key="title",
        label="Hofbräuhaus München",
        value="ECCA Conference 2025 - Gala Dinner",
        semantics=EventTicketSemanticTags(
            venueLocation=Location(
                latitude=48.1371,
                longitude=11.5753,
            ),
            venueName="Hofbräuhaus München",
            # venueAddress="Platzl 9, 80331 München",  # venueAddress gibts nicht
        ),
    )

    with pytest.raises(ValidationError):
        passes.SemanticPassFieldContent(
            key="title",
            label="Hofbräuhaus München",
            value="ECCA Conference 2025 - Gala Dinner",
            semantics=EventTicketSemanticTags(
                venueLocation=Location(
                    latitude=48.1371,
                    longitude=11.5753,
                ),
                venueName="Hofbräuhaus München",
                venueAddress="Platzl 9, 80331 München",  # venueAddress gibts nicht
            ),
        )

    sp = passes.SemanticPassFieldContent.model_validate(
        {
            "key": "eventdate",
            "value": "2025-05-27T19:30+02:00",
            "label": "Date",
            "dateStyle": "PKDateStyleLong",
            "timeStyle": "PKDateStyleShort",
            "semantics": {
                "eventStartDate": "2025-05-27T19:30+02:00",
                "eventEndDate": "2025-05-27T23:00+02:00",
            },
        }
    )

    print(sp)


def test_semantic_tags1():
    d = {
        "eventType": "PKEventTypeSocialGathering",
        "silenceRequested": True,
        "eventName": "ECCA Conference 2025 - Gala Dinner",
        "eventStartDate": "2025-05-27T19:00+02:00",
        "eventEndDate": "2025-05-27T23:00+02:00",
        "venueLocation": {"latitude": 48.1371, "longitude": 11.5753},
        "venueName": "Hofbräuhaus München",
        "venueRoom": "Wappensaal",
        "attendeeName": "Alexander Loechel",
        "admissionLevel": "ECCA Conference 2025 - Gala Dinner",
    }

    EventTicketSemanticTags.model_validate(d)


def test_semantic_tags2():
    passes.SemanticPassFieldContent(
        key="address",
        value="Ludwig-Maximilians-Universität München\nGeschwister-Scholl-Platz 1\n80539 München",
        label="Address / Venue",
        semantics=EventTicketSemanticTags(
            venueLocation=semantic_tags.Location(
                latitude=48.1508563, longitude=11.5800829
            ),
            venueName="Ludwig-Maximilians-Universität München",
            venueRoom="Senatssaal",
        ),
    )


def test_event_pass_semantic_tags(passes_json_dir):
    buf = open(passes_json_dir / "event_ticket.json").read()
    pass1 = passes.Pass.model_validate_json(buf)

    card_info = pass1.pass_information

    # build fields from json
    card_info.headerFields = [
        passes.SemanticPassFieldContent.model_validate(
            {
                "key": "eventdate",
                "value": "2025-05-27T19:30+02:00",
                "label": "Date",
                "dateStyle": "PKDateStyleLong",
                "timeStyle": "PKDateStyleShort",
                "semantics": {
                    "eventStartDate": "2025-05-27T19:30+02:00",
                    "eventEndDate": "2025-05-27T23:00+02:00",
                },
            }
        )
    ]

    print(pass1.model_dump(exclude_none=True))

    # build fields by api call
    card_info.primaryFields = [
        passes.SemanticPassFieldContent(
            key="title",
            label="Hofbräuhaus München",
            value="ECCA Conference 2025 - Gala Dinner",
            semantics=EventTicketSemanticTags(
                venueLocation=Location(
                    latitude=48.1371,
                    longitude=11.5753,
                ),
                venueName="Hofbräuhaus München",
                # venueAddress="Platzl 9, 80331 München",  # venueAddress gibts nicht
            ),
        )
    ]

    backFields_json = [
        {
            "key": "start",
            "value": "2025-05-27T19:30+02:00",
            "label": "Event start",
            "dateStyle": "PKDateStyleLong",
            "timeStyle": "PKDateStyleShort",
            "semantics": {
                "eventStartDate": "2025-05-26T19:00+02:00",
            },
        },
        {
            "key": "end",
            "value": "2025-05-27T23:00+02:00",
            "label": "Event end",
            "dateStyle": "PKDateStyleLong",
            "timeStyle": "PKDateStyleShort",
            "semantics": {
                "eventEndDate": "2025-05-26T21:00+02:00",
            },
        },
        {
            "key": "address",
            "value": "Hofbräuhaus München\nPlatzl 9\n80331 München",
            "label": "Address / Venue",
            "semantics": {
                "venueLocation": {
                    "latitude": 48.1371,
                    "longitude": 11.5753,
                },
                "venueName": "Hofbräuhaus München",
                "venueRoom": "Wappensaal",
                # "venueAddress": "Platzl 9, 80331 München",
            },
        },
        {
            "key": "program",
            "value": '<a href="https://conference.ecca.eu/conference#timeline">Program ECCA Conference 2025</a>',
            "label": "Program",
            "semantics": {
                "additionalTicketAttributes": "https://conference.ecca.eu/conference#timeline"  # contactVenueWebsite gibts nicht
            },
        },
    ]

    card_info.backFields = [
        passes.SemanticPassFieldContent.model_validate(backField)
        for backField in backFields_json
    ]

    pass_json = pass1.model_dump(exclude_none=True)

    assert pass_json["eventTicket"]["headerFields"][0]["key"] == "eventdate"


def test_ecca_gala_dinner():
    apple_passes = passes
    pass_type_identifier = "pass.ecca.eu.gala.dinner"
    pass_id = "21313123123123123123"

    def create_pkpass():

        ticket_holder = "Donald Duck"
        ticket_number = "1234567890"
        organization = "European Campus Card Association"

        card_info = apple_passes.EventTicket()
        card_info.headerFields = [
            passes.SemanticPassFieldContent.model_validate(
                {
                    "key": "eventdate",
                    "value": "2025-05-27T19:30+02:00",
                    "label": "Date",
                    "dateStyle": "PKDateStyleLong",
                    "timeStyle": "PKDateStyleShort",
                    "semantics": {
                        "eventStartDate": "2025-05-27T19:30+02:00",
                        "eventEndDate": "2025-05-27T23:00+02:00",
                    },
                }
            )
        ]
        card_info.primaryFields = [
            passes.SemanticPassFieldContent.model_validate(
                {
                    "key": "title",
                    "label": "Hofbräuhaus München",
                    "value": "ECCA Conference 2025 - Gala Dinner",
                    "semantics": {
                        "venueLocation": {
                            "latitude": 48.1371,
                            "longitude": 11.5753,
                        },
                        "venueName": "Hofbräuhaus München",
                        "additionalTicketAttributes": "Platzl 9, 80331 München",  # venueAddress gibts nicht
                    },
                }
            )
        ]
        card_info.addSecondaryField(
            key="holder",
            value=ticket_holder,
            label="Ticketholder",
        )
        card_info.addAuxiliaryField(
            key="org",
            value=organization,
            label="Organization",
        )
        card_info.backFields = [
            apple_passes.SemanticPassFieldContent.model_validate(bf)
            for bf in [
                {
                    "key": "start",
                    "value": "2025-05-27T19:30+02:00",
                    "label": "Event start",
                    "dateStyle": "PKDateStyleLong",
                    "timeStyle": "PKDateStyleShort",
                    "semantics": {
                        "eventStartDate": "2025-05-26T19:00+02:00",
                    },
                },
                {
                    "key": "end",
                    "value": "2025-05-27T23:00+02:00",
                    "label": "Event end",
                    "dateStyle": "PKDateStyleLong",
                    "timeStyle": "PKDateStyleShort",
                    "semantics": {
                        "eventEndDate": "2025-05-26T21:00+02:00",
                    },
                },
                {
                    "key": "address",
                    "value": "Hofbräuhaus München\nPlatzl 9\n80331 München",
                    "label": "Address / Venue",
                    "semantics": {
                        "venueLocation": {
                            "latitude": 48.1371,
                            "longitude": 11.5753,
                        },
                        "venueName": "Hofbräuhaus München",
                        "venueRoom": "Wappensaal",
                        "additionalTicketAttributes": "Platzl 9, 80331 München",  # venuAddress gibts nicht
                    },
                },
                {
                    "key": "homepage_conference",
                    "value": '<a href="https://conference.ecca.eu/">Homepage ECCA Conference 2025</a>',
                    "label": "Conference Information",
                },
                {
                    "key": "program",
                    "value": '<a href="https://conference.ecca.eu/conference#timeline">Program ECCA Conference 2025</a>',
                    "label": "Program",
                    "semantics": {
                        "additionalTicketAttributes": "https://conference.ecca.eu/conference#timeline"  # contactVenueWebsite gibts nicht
                    },
                },
                {
                    "key": "homepage_ecca",
                    "value": '<a href="https://ecca.eu/">Homepage ECCA</a>',
                    "label": "Homepage ECCA",
                },
                {
                    "key": "homepage_edutap",
                    "value": '<a href="https://eduTAP.eu/">eduTAP Homepage</a>',
                    "label": "issued using eduTAP",
                },
                {
                    "key": "contact_sinead_mail",
                    "value": '<a href="mailto:info@ecca.eu">info@ecca.eu</a>',
                    "label": "Organizer Contact",
                },
                {
                    "key": "contact_sinead_phone",
                    "value": '<a href="tel:+353872572418">Call Organizer Contact (Sinead Nealon; ECCA)</a>',
                },
                {
                    "key": "contact_alexander",
                    "value": '<a href="tel:+4915203516751">Call Organizer Contact (Alexander Loechel; LMU München)</a>',
                },
                {
                    "key": "contact_group",
                    "value": '<a href="https://chat.whatsapp.com/F76MRvZxuz6K9zLWdLctrf">ECCA 2025 Munich - WhatsApp Community</a>',
                },
            ]
        ]

        pass_model = passes.Pass(
            eventTicket=card_info,
            organizationName="European Campus Card Association",
            passTypeIdentifier=pass_type_identifier,
            teamIdentifier="ANA-U",
            serialNumber=pass_id,
            description="ECCA Conference 2025 Gala Dinner Ticket",
            relevantDate="2025-05-27T17:00+02:00",
            expirationDate="2025-05-27T23:30+02:00",
            locations=[
                apple_datatypes.Location(
                    latitude=48.1371,
                    longitude=11.5753,
                    # distance=1000.0,  #distance gibts nicht
                    relevantText="Welcome to the Gala Dinner of the ECCA Conference 2025",
                )
            ],
            groupingIdentifier="2025.ecca.eu",
            sharingProhibited=True,
        )

        pass_model.semantics = EventTicketSemanticTags.model_validate(
            {
                "eventType": "PKEventTypeSocialGathering",
                "silenceRequested": True,
                "eventName": "ECCA Conference 2025 - Gala Dinner",
                "venueLocation": {
                    "latitude": 48.1371,
                    "longitude": 11.5753,
                },
                "venueName": "Hofbräuhaus München",
                "additionalTicketAttributes": "Platzl 9, 80331 München",  # venueAddress gibts nicht
                "eventStartDate": "2025-05-27T19:00+02:00",
                "eventEndDate": "2025-05-27T23:00+02:00",
            }
        )

        pass_model.backgroundColor = "#1A80C3"
        pass_model.foregroundColor = "#FFFFFF"
        pass_model.labelColor = "#F5F5F5"
        pass_model.backgroundColor = "#1A80C3"
        pass_model.foregroundColor = "#FFFFFF"
        pass_model.labelColor = "#F5F5F5"
        pass_model.useAutomaticColors = True

        pass_model.nfc = apple_passes.NFC(
            message=ticket_number,
            encryptionPublicKey="MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgACjAjiWfWMSPxNXZvxyaSgsg7bPmUpnd9BVoGUwryk7m0=",
        )

        pkpass = apple_api.new(data=pass_model)

        return pkpass

    pkpass = create_pkpass()

    pkpass_json = pkpass._pass_json
    pkpass1 = apple_api.new(data=json.loads(pkpass_json))

    assert pkpass1 is not None


def test_sports_event():
    apple_passes = passes
    pass_type_identifier = "pass.ecca.eu.gala.dinner"
    pass_id = "21313123123123123123"

    def create_pkpass():
        ticket_holder = "Donald Duck"
        ticket_number = "1234567890"
        organization = "European Campus Card Association"

        card_info = apple_passes.EventTicket()
        card_info.headerFields = [
            apple_passes.SemanticPassFieldContent(
                key="eventdate",
                value="26-28 May, 2025",
                label="Date",
                semantics=EventTicketSemanticTags(
                    eventName="ECCA Conference 2025",
                    eventStartDate="2025-05-27T09:00+02:00",
                    eventEndDate="2025-05-28T14:00+02:00",
                ),
            )
        ]
        card_info.primaryFields = [
            apple_passes.SemanticPassFieldContent(
                key="title",
                value="ECCA Conference 2025",
                label="Ludwig-Maximilians-Universität München",
                semantics=EventTicketSemanticTags(
                    eventName="ECCA Conference 2025",
                    eventStartDate="2025-05-27T09:00+02:00",
                    eventEndDate="2025-05-28T14:00+02:00",
                ),
            ),
        ]

        card_info.secondaryFields = [
            apple_passes.SemanticPassFieldContent(
                key="holder",
                value=ticket_holder,
                label="Ticketholder",
                semantics=EventTicketSemanticTags(
                    attendeeName=ticket_holder,
                ),
            ),
        ]

        card_info.auxiliaryFields = [
            apple_passes.SemanticPassFieldContent(
                key="org",
                value=organization,
                label="Organization",
            ),
        ]

        card_info.backFields = [
            apple_passes.SemanticPassFieldContent(
                key="start",
                value="2025-05-27T09:00+02:00",
                label="Event start",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
                semantics=EventTicketSemanticTags(
                    eventStartDate="2025-05-27T09:00+02:00",
                ),
            ),
            apple_passes.SemanticPassFieldContent(
                key="end",
                value="2025-05-28T14:00+02:00",
                label="Event end",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
                semantics=EventTicketSemanticTags(
                    eventEndDate="2025-05-28T14:00+02:00",
                ),
            ),
            apple_passes.SemanticPassFieldContent(
                key="registration_open",
                value="2025-05-27T08:30+02:00",
                label="Registration opens",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="welcome_reception",
                value="2025-05-26T19:00+02:00",
                label="Welcome Reception",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="tuesday_start",
                value="2025-05-27T09:00+02:00",
                label="1st Conference Day starts at",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="tuesday_end",
                value="2025-05-27T17:00+02:00",
                label="1st Conference Day ends at",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="conference_dinner",
                value="2025-05-27T19:30+02:00",
                label="Gala Dinner at Hofbräuhaus starts at",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="wednesday_start ",
                value="2025-05-28T09:00+02:00",
                label="2nd Conference Day starts at",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="wednesday_end ",
                value="2025-05-28T14:00+02:00",
                label="2nd Conference Day ends at",
                dateStyle="PKDateStyleLong",
                timeStyle="PKDateStyleShort",
            ),
            apple_passes.SemanticPassFieldContent(
                key="address",
                value="Ludwig-Maximilians-Universität München\nGeschwister-Scholl-Platz 1\n80539 München",
                label="Address / Venue",
                semantics=EventTicketSemanticTags(
                    venueLocation=SemanticLocation(
                        latitude=48.1508563, longitude=11.5800829
                    ),
                    venueName="Ludwig-Maximilians-Universität München",
                    venueRoom="Senatssaal",
                ),
            ),
            apple_passes.SemanticPassFieldContent(
                key="homepage_conference",
                value='<a href="https://conference.ecca.eu/">Homepage ECCA Conference 2025</a>',
                label="Conference Information",
            ),
            apple_passes.SemanticPassFieldContent(
                key="homepage_conference",
                value='<a href="https://conference.ecca.eu/">Homepage ECCA Conference 2025</a>',
                label="Conference Information",
            ),
            apple_passes.SemanticPassFieldContent(
                key="homepage_ecca",
                value='<a href="https://ecca.eu/">Homepage ECCA</a>',
                label="Homepage ECCA",
            ),
            apple_passes.SemanticPassFieldContent(
                key="homepage_edutap",
                value='<a href="https://eduTAP.eu/">eduTAP Homepage</a>',
                label="issued using eduTAP",
            ),
            apple_passes.SemanticPassFieldContent(
                key="contact_sinead_mail",
                value='<a href="mailto:info@ecca.eu">info@ecca.eu</a>',
                label="Organizer Contact",
            ),
            apple_passes.SemanticPassFieldContent(
                key="contact_sinead_phone",
                value='<a href="tel:+353872572418">Call Organizer Contact (Sinead Nealon; ECCA)</a>',
            ),
            apple_passes.SemanticPassFieldContent(
                key="contact_alexander",
                value='<a href="tel:+4915203516751">Call Organizer Contact (Alexander Loechel; LMU München)</a>',
            ),
            apple_passes.SemanticPassFieldContent(
                key="contact_group",
                value='<a href="https://chat.whatsapp.com/F76MRvZxuz6K9zLWdLctrf">ECCA 2025 Munich - WhatsApp Community</a>',
            ),
        ]

        card_info.additionalInfoFields = [
            apple_passes.PassFieldContent(
                key="program",
                value="Ana-U · Elatec · Entrust · OPTeam",
                label="Premium Sponsors",
            ),
        ]

        pass_model = apple_passes.Pass(
            eventTicket=card_info,
            organizationName="European Campus Card Association",
            passTypeIdentifier=pass_type_identifier,
            teamIdentifier="FH8UJ9LP38",
            serialNumber=pass_id,
            description="ECCA Conference 2025 Ticket",
            relevantDates=[
                apple_passes.RelevantDate(
                    startDate="2025-05-27T08:00+02:00",
                    endDate="2025-05-27T17:30+02:00",
                ),
                apple_passes.RelevantDate(
                    startDate="2025-05-28T08:00+02:00",
                    endDate="2025-05-28T15:00+02:00",
                ),
            ],
            expirationDate="2025-05-28T18:00+02:00",
            locations=[
                apple_datatypes.Location(
                    latitude=48.1508563,
                    longitude=11.5800829,
                    distance=1000.0,
                    relevantText="Welcome to ECCA Conference 2025",
                )
            ],
            groupingIdentifier="2025.ecca.eu",
            sharingProhibited=True,
            preferredStyleSchemes=["posterEventTicket", "eventTicket"],
            contactVenueWebsite="https://conference.ecca.eu/conference#timeline",
            merchandiseURL="https://conference.ecca.eu/conference#timeline",
            orderFoodURL="https://conference.ecca.eu/conference#timeline",
        )

        pass_model.semantics = EventTicketSemanticTags(
            eventType="PKEventTypeConference",
            silenceRequested=True,
            eventName="ECCA Conference 2025",
            eventStartDate="2025-05-27T09:00+02:00",
            eventEndDate="2025-05-28T14:00+02:00",
            venueName="Ludwig-Maximilians-Universität München",
            venueRoom="Senatssaal",
            venueLocation=SemanticLocation(latitude=48.1508563, longitude=11.5800829),
            attendeeName=ticket_holder,
            admissionLevel="ECCA Conference 2025",
        )

        pass_model.backgroundColor = "#1A80C3"
        pass_model.foregroundColor = "#FFFFFF"
        pass_model.labelColor = "#F5F5F5"
        pass_model.useAutomaticColors = True
        pass_model.footerBackgroundColor = "#1A80C3"

        pass_model.nfc = apple_passes.NFC(
            message=ticket_number,
            encryptionPublicKey="MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgAD+nUs+qnI0EG8GVt01Ijjjqcg+KdU3OLGQDmGz4mYfcM=",
        )

        pkpass = apple_api.new(data=pass_model)
        return pkpass
 
    pkpass = create_pkpass()

    pkpass_json = pkpass._pass_json
    pkpass1 = apple_api.new(data=json.loads(pkpass_json))

    assert pkpass1 is not None
