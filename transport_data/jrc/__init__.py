import sdmx.model.v21 as m


def get_agency() -> m.Agency:
    # Agency
    a = m.Agency(
        id="JRC",
        name="Joint Research Centre of the European Commission",
        description="""See https://joint-research-centre.ec.europa.eu/index_en.

Maintainers of the IDEES data set: https://data.jrc.ec.europa.eu/dataset/jrc-10110-10001""",  # noqa: E501
    )

    return a
