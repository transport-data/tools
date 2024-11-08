import pytest

from transport_data.iso import get_cl_iso_3166_1


@pytest.mark.parametrize(
    "id_field, entries",
    (
        ("alpha_2", ("AW", "ZE")),
        ("alpha_3", ("ABW", "ZWE")),
        ("numeric", ("533", "716")),
    ),
)
def test_get_cl_iso_3166_1(id_field, entries) -> None:
    result = get_cl_iso_3166_1(id_field=id_field)

    # Result has the expected number of codes
    assert 249 == len(result)

    # The name of Aruba is localized in 58 languages
    assert 58 == len(result[entries[0]].name.localizations)
