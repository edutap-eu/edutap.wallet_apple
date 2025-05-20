from edutap.wallet_apple.models import passes
from edutap.wallet_apple.models.semantic_tags import Location, SemanticTags


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
            semantics=SemanticTags(
                venueLocation=Location(
                    latitude=48.1371,
                    longitude=11.5753,
                ),
                venueName="Hofbräuhaus München",
                venueAddress="Platzl 9, 80331 München",
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
                "venueAddress": "Platzl 9, 80331 München",
            },
        },
        {
            "key": "program",
            "value": '<a href="https://conference.ecca.eu/conference#timeline">Program ECCA Conference 2025</a>',
            "label": "Program",
            "semantics": {
                "contactVenueWebsite": "https://conference.ecca.eu/conference#timeline"
            },
        },
    ]

    card_info.backFields = [
        passes.SemanticPassFieldContent.model_validate(backField)
        for backField in backFields_json
    ]

    pass_json = pass1.model_dump(exclude_none=True)

    assert pass_json["eventTicket"]["headerFields"][0]["key"] == "eventdate"
