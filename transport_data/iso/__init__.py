"""International Organization for Standardization (ISO)."""

import logging
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Mapping

from sdmx.model import common

from transport_data.util.pluggy import hookimpl

if TYPE_CHECKING:
    import gettext

log = logging.getLogger(__name__)


@hookimpl
def get_agencies():
    """Return the ``ISO`` :class:`~.sdmx.model.common.Agency`."""
    a = common.Agency(
        id="ISO",
        name="International Organization for Standardization",
        contact=[common.Contact(uri=["https://iso.org"])],
    )
    return (a,)


def get_cl_iso_3166_1(
    id_field: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2",
) -> common.Codelist:
    """Generate a :class:`~sdmx.model.common.Codelist` with entries from ISO 3166-1.

    Codes have:

    - IDs according to `id_field`.
    - An :attr:`~sdmx.model.common.IdentifiableArtefact.name` attribute localized to all
      the languages present in the upstream database.

    Parameter
    ---------
    id_field :
        Field from the database to use for the IDs of generated Codes.
    """
    from importlib.metadata import version

    import sdmx.urn
    from pycountry import countries as db

    from transport_data import STORE

    # Create an empty codelist
    cl: common.Codelist = common.Codelist(
        id=f"{db.root_key}_{id_field}",
        maintainer=get_agencies()[0],
        version=version("pycountry"),
    )

    # Load localizations of this code list
    translations = load_translations(f"iso{db.root_key}")

    # Convert all entries in the database to SDMX Codes
    for data in db:
        # Collect localizations of the country name
        name = localize_all(data.name, translations)
        # TODO Collect localizations of other fields; add as annotations
        # TODO Annotate with other non-localized fields

        # Create a Code
        c = common.Code(id=getattr(data, id_field), name=name)
        # Append to the code list
        cl.append(c)

        # Generate its URN
        c.urn = sdmx.urn.make(c)

    # Write to local store
    STORE.set(cl)

    return cl


def localize_all(value: str, translations, *, default_locale="en") -> dict[str, str]:
    """Localize `value` in all languages available in `translations`."""
    # Put the default locale first
    result = {default_locale: value}

    for lang, tr in translations.items():
        localized = tr.gettext(value)
        if localized != value:
            result[lang] = localized

    return result


@lru_cache
def load_translations(domain: str) -> Mapping[str, "gettext.NullTranslations"]:
    """Load all available :mod:`pycountry` translations for `domain`."""
    from gettext import translation

    from pycountry import LOCALES_DIR

    result = {}
    for lang in map(lambda d: d.name, Path(LOCALES_DIR).iterdir()):
        try:
            result[lang] = translation(domain, LOCALES_DIR, languages=[lang])
        except FileNotFoundError:
            pass

    return result
