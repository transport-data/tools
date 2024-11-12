"""Other data providers."""

from transport_data.util.pluggy import hookimpl


@hookimpl
def get_agencies():
    from sdmx.model.common import Agency, Contact

    a0 = Agency(
        id="GAIKINDO",
        name={
            "en": "The Association of Indonesia Automobile Industries",
            "id": "Gabungan Industri Kendaraan Bermotor Indonesia",
        },
        contact=[
            Contact(
                uri=[
                    "https://www.gaikindo.or.id",
                    "https://www.gaikindo.or.id/indonesian-automobile-industry-data/",
                ]
            )
        ],
    )
    a1 = Agency(
        id="TAIA",
        name={
            "en": "The Thai Automotive Industry Association",
            "th": "สมาคมอุตสาหกรรมยานยนต์ไทย",
        },
        contact=[Contact(uri=["https://taia.or.th", "https://taia.or.th/en/"])],
    )

    return (a0, a1)
