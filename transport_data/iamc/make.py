from typing import Optional

import sdmx.model.v21 as m


def make_variables_cl(
    dsd: m.BaseDataStructureDefinition, codelist: Optional[m.Codelist] = None
):
    """Generate an SDMX codelist with IAMC-style "variable" names from `dsd`."""

    cl = codelist or m.Codelist(id="VARIABLE")

    for key in dsd.iter_keys():
        # Parts of the variable ID; full key as (str -> str)
        var_parts, full_key = [str(dsd.measures[0].concept_identity.name)], {}

        # Iterate over KeyValues
        for dim, kv in key.values.items():
            if kv.value.id == "_T":
                # Total: pass through
                var_parts.append("_T")
            else:
                # Use the (human-readable) name
                var_parts.append(str(kv.value.name))
            full_key[kv.value_for.id] = kv.value.id

        # - Join var_parts with the IAMC "|" character.
        # - Remove "|_T" to yield IAMC-style names for aggregates.
        variable = "|".join(var_parts).replace("|_T", "")

        # Create a Code
        # - ID is the variable name.
        # - Annotate with iamc-full-dsd = URN of the full DSD.
        # - Annotate with iamc-full-key = representation of the full key.
        cl.append(
            m.Code(
                id=variable,
                annotations=[
                    m.Annotation(id="iamc-full-dsd", text=dsd.urn),
                    m.Annotation(id="iamc-full-key", text=repr(full_key)),
                ],
            )
        )

    return cl
