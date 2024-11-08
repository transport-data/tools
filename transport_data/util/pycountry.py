"""Utilities for working with pycountry_.

.. _pycountry: https://pypi.org/project/pycountry/
"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    import gettext

    import pycountry.db

#: Fields in the :mod:`.pycountry` databases for which localizations are available.
LOCALIZABLE = {
    "name",
    "official_name",
}

#: Mapping from country name forms appearing in data to values recognized by
#: :meth:`pycountry.countries.lookup`.
NAME_MAP = {
    "russia": "RU",  # "Russian Federation"
    "turkey": "TR",  # "Türkiye"
}


@dataclass
class DatabaseInfo:
    """Information about a :mod:`pycountry` database."""

    #: Name of the variable in the :mod:`pycountry` namespace.
    name: str
    #: Matches :attr:`pycountry.db.Database.root_key`.
    root_key: str
    #: Fields which can be used as code IDs.
    id_fields: set[str]


#: Information on the databases of :mod:`pycountry`.
DATABASE_INFO = (
    DatabaseInfo("countries", "3166-1", {"alpha_2", "alpha_3", "numeric"}),
    DatabaseInfo("subdivisions", "3166-2", {"code"}),
    DatabaseInfo(
        "historic_countries", "3166-3", {"alpha_2", "alpha_3", "alpha_4", "numeric"}
    ),
    DatabaseInfo("currencies", "4217", {"alpha_3", "numeric"}),
    DatabaseInfo("languages", "639-3", {"alpha_2", "alpha_3"}),
    DatabaseInfo("language_families", "639-5", {"alpha_3"}),
    DatabaseInfo("scripts", "15924", {"alpha_4", "numeric"}),
)


@lru_cache
def get_database(standard_number: str) -> tuple["pycountry.db.Database", DatabaseInfo]:
    """Retrieve a :mod:`pycountry` database given its ISO `standard_number`."""
    import pycountry

    for info in DATABASE_INFO:
        if info.root_key == standard_number:
            return getattr(pycountry, info.name), info

    raise ValueError(standard_number)


@lru_cache
def load_translations(domain: str) -> Mapping[str, "gettext.NullTranslations"]:
    """Load all available :mod:`pycountry` translations for `domain`."""
    from gettext import translation

    from pycountry import LOCALES_DIR

    # Iterate over all subdirectories of the pycountry locale dir
    result = {}
    for lang in map(lambda d: d.name, Path(LOCALES_DIR).iterdir()):
        try:
            result[lang] = translation(domain, LOCALES_DIR, languages=[lang])
        except FileNotFoundError:
            pass  # No translations for this (domain, lang)

    return result
