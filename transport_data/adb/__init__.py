import sdmx.model.v21 as m


def get_agency() -> m.Agency:
    # Agency
    a = m.Agency(
        id="ADB",
        name="Asian Transport Outlook team at the Asian Development Bank",
        description="""See https://www.adb.org/what-we-do/topics/transport/asian-transport-outlook""",  # noqa: E501
    )

    return a
