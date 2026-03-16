import pytest

from transport_data.iso import generate_all


@pytest.fixture(scope="session")
def all_generated():
    """All ISO code lists generated in the test data directory."""
    generate_all()


def test_generate_all(all_generated):
    from transport_data import STORE

    urns = STORE.list(maintainer="ISO")

    # At least 15 code lists were generated
    assert 15 <= len(urns)


@pytest.mark.parametrize(
    "standard_number, id_field, N_exp, entries, N_tr",
    (
        ("639-3", "alpha_2", 184, ("aa", "zu"), 59),
        ("639-3", "alpha_3", 7923, ("aaa", "zzj"), 21),
        #
        ("639-5", "alpha_3", 115, ("aav", "znd"), 37),
        #
        ("3166-1", "alpha_2", 249, ("AW", "ZE"), 60),
        ("3166-1", "alpha_3", 249, ("ABW", "ZWE"), 60),
        ("3166-1", "numeric", 249, ("533", "716"), 60),
        #
        ("3166-2", "code", 5046, ("AD-02", "ZW-MW"), 17),
        #
        ("3166-3", "alpha_2", 30, ("AI", "ZR"), 83),
        ("3166-3", "alpha_3", 31, ("AFI", "ZAR"), 83),
        ("3166-3", "alpha_4", 31, ("AIDJ", "ZRCD"), 83),
        ("3166-3", "numeric", 25, ("262", "180"), 83),
        #
        ("4217", "alpha_3", 178, ("AED", "ZWL"), 59),
        ("4217", "numeric", 178, ("784", "932"), 59),
        #
        ("15924", "alpha_4", 226, ("Adlm", "Zzzz"), 32),
        ("15924", "numeric", 226, ("166", "999"), 32),
    ),
)
def test_generate_codelist(
    all_generated,
    # Function arguments
    standard_number: str,
    id_field: str,
    # Expected values
    N_exp: int,  # Total number of items
    entries: tuple[str, ...],  # IDs of some items
    N_tr: int,  # Number of localizations for the name of the first of `entries`
) -> None:
    from transport_data import STORE

    # The code list is available with the expected URL
    cl = STORE.get(f"Codelist=ISO:{standard_number}_{id_field}")

    # Result has the expected number of codes
    assert N_exp == len(cl)

    # The name of the first of `entries` is localized in `N_tr` languages
    assert N_tr == len(cl[entries[0]].name.localizations)
