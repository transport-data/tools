import sdmx.model.v21 as m


def get_agency() -> m.Agency:
    # Agency
    a = m.Agency(
        id="ADB",
        name="Asian Transport Outlook team at the Asian Development Bank",
        description="""See https://www.adb.org/what-we-do/topics/transport/asian-transport-outlook""",  # noqa: E501
    )

    c1 = m.Contact(name="James Leather", email=["jleather@adb.org"])
    c2 = m.Contact(name="Cornie Huizenga", email=["chuizenga@cesg.biz"])
    c3 = m.Contact(name="Sudhir Gota", email=["sudhirgota@gmail.com"])
    a.contact.extend([c1, c2, c3])

    return a
