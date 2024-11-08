"""International Organization for Standardization (ISO)."""

import logging
from functools import partial
from typing import TYPE_CHECKING, Mapping

from sdmx.model import common

from transport_data.util.pluggy import hookimpl
from transport_data.util.pycountry import LOCALIZABLE, get_database, load_translations

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


def generate_all() -> None:
    """Generate codelists for all the databases in :data:`.pycountry.DATABASE_INFO`."""
    from transport_data.util.pycountry import DATABASE_INFO

    for info in DATABASE_INFO:
        generate_codelists(standard_number=info.root_key)


def generate_codelists(standard_number: str) -> None:
    """Generate 1 or more :class:`.Codelist` with entries from ISO `standard_number`.

    Codes have:

    - IDs according to `id_field`.
    - An :attr:`~sdmx.model.common.IdentifiableArtefact.name` attribute localized to all
      the languages present in the upstream database.
    - Annotations for all other fields in the upstream database.

    Parameters
    ----------
    standard_number :
        ISO standard number, e.g. "3166-2" for ISO 3166-2.
    """
    from importlib.metadata import version

    import sdmx.urn

    from transport_data import STORE

    db, info = get_database(standard_number)

    # Load localizations for this standard number
    tr = partial(localize_all, translations=load_translations(f"iso{db.root_key}"))

    # Create 1 or more empty code lists: 1 for each possible id_field
    kw = dict(maintainer=get_agencies()[0], version=version("pycountry"))
    cl: dict[str, common.Codelist] = {
        f: common.Codelist(id=f"{db.root_key}_{f}", **kw) for f in info.id_fields
    }

    # Convert all entries in the database to SDMX Codes
    for record in db:
        # - Iterate over all fields in the record.
        # - For localizable fields, collect localizations of the field's value.
        # - Convert to Annotation objects. Not all of these will be used for each Code.
        anno = {
            f: common.Annotation(id=f, text=tr(v) if f in LOCALIZABLE else {"zxx": v})
            for f, v in record._fields.items()
            if v is not None
        }

        # Add one code to cl["alpha_2"] with an alpha_2 ID, one to cl["alpha_3"] with an
        # alpha_3 ID, etc.
        for id_field in info.id_fields:
            try:
                id_ = anno[id_field].text.localized_default()
            except KeyError:
                log.info(f"No {id_field!r} field → omit:\n{record}")
                continue

            # Create a code
            c = common.Code(
                id=id_,
                name=anno["name"].text,
                annotations=[v for f, v in anno.items() if f not in {"name", id_field}],
            )

            # Append to the respective code list
            try:
                cl[id_field].append(c)
            except ValueError:
                log.info(
                    f"ID {id_!r} duplicates existing entry {cl[id_field][id_]!r} → omit"
                    f"\n{record}"
                )
                continue

            # Generate its URN
            c.urn = sdmx.urn.make(c)

    # Write to local store
    for codelist in cl.values():
        STORE.set(codelist)


def localize_all(
    value: str,
    translations: Mapping[str, "gettext.NullTranslations"],
    *,
    default_locale="en",
) -> dict[str, str]:
    """Localize `value` in all languages available in `translations`."""
    # Put the default locale first
    result = {default_locale: value}

    for lang, tr in translations.items():
        localized = tr.gettext(value)
        if localized != value:
            result[lang] = localized

    return result
