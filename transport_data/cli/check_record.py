from collections import defaultdict
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from pathlib import Path

    from sdmx.model.v30 import Dataflow

    from transport_data.util.ckan import Package


@click.command("check-record")
@click.argument("id")
def main(id: str) -> None:
    """Check record NAME on the TDC."""
    # TODO Use .org.ckan.instance_option
    from transport_data.org.ckan import PROD

    # Retrieve the record, converted to an instance of Package
    package = PROD.package_show(id)

    # Print general package information
    print(
        f"{package!r}",
        package.portal_url(),
        f"Title: {package.title!r}",
        f"Category: {package.tdc_category}",
        sep="\n- ",
    )

    check_package0(package)


SUFFIXES = {
    "data": {".xlsx", ".csv"},
}


def check_package0(package: "Package") -> None:
    """Print some checks about a `package`."""
    from transport_data.util.sdmx import structure_from_csv

    # Mapping from Path instances to args for read_csv() or None
    file_args: dict["Path", tuple["Dataflow", dict] | None] = {}

    # Counts of suffixes
    suffix_count: MutableMapping[str, int] = defaultdict(lambda: 0)
    for resource in package.resources:
        # Fetch a local copy of the resource; return its path
        path = resource.fetch()

        # Count the file suffix
        suffix_lower = path.suffix.lower()
        suffix_count[suffix_lower] += 1

        try:
            # Infer a data structure definition from the file
            file_args[path] = structure_from_csv(path)
        except Exception:
            # Not a CSV file or cannot infer a DSD
            file_args[path] = None
            continue

    @dataclass
    class Check:
        label: str
        value: Any

        def __str__(self) -> str:
            return f"{self.label}: {self.value}"

    c0 = Check(
        "Number of files by extension",
        ", ".join(f"{c} {s}" for s, c in sorted(suffix_count.items())),
    )
    c1 = Check(
        "Number of data files",
        sum(c for s, c in suffix_count.items() if s in SUFFIXES["data"]),
    )
    c2 = Check("Number of possible SDMX-CSV files", suffix_count[".csv"])
    checks = [c0, c1, c2]

    lines = [""] + [f"- {check}" for check in checks] + [""]

    lines.append("Criteria for a TDC Formatted record:")
    c3 = Check("At least one file in CSV format", c2.value >= 1)
    c4 = Check(
        "Correct category assigned",
        package.tdc_category in {"tdc_formatted", "tdc_harmonized"},
    )
    c5 = Check("≥1 CSV file is in SDMX-CSV format", any(map(bool, file_args.values())))
    c6 = Check("Overall", "YES" if (c3.value and c4.value and c5.value) else "NO")

    lines.extend(f"- {check}" for check in (c3, c4, c5, c6))

    lines.extend(["", "Criteria for a TDC Harmonized record—all of the above, plus:"])
    c7 = Check(
        "Data structure dimension IDs are all in TDCI:CS_CONCEPTS (not implemented yet)",
        True,
    )
    c8 = Check("Correct category assigned", package.tdc_category == "tdc_harmonized")
    c9 = Check("Overall", "YES" if (c7.value and c8.value) else "NO")

    lines.extend(f"- {check}" for check in (c7, c8, c9))

    print(*lines, sep="\n")
