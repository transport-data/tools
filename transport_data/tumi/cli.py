from enum import Enum, auto
from itertools import chain
from pathlib import Path

import click


@click.group("tumi", short_help="TUMI provider.")
def main() -> None:
    """Transforming Urban Mobility Initiative (TUMI) provider."""


@main.command("import")
@click.argument("path", type=click.Path(dir_okay=True, readable=True, path_type=Path))
def import_(path: Path) -> None:
    """Import data from an export.

    The tool expects a single argument with the path of a directory. The directory MUST
    contain the following:

    \b
    datasets.jsonlines
    ckan/
      resources/
         000/
           000/
             00-a1b2-c3d4-e5f6-a7b8c9d0e1f2
    """
    import json

    from transport_data.util.ckan import Package

    # Path to datasets.json
    datasets_path = path.joinpath("datasets.jsonlines")
    resources_path = path.joinpath("ckan", "resources")
    assert datasets_path.exists() and resources_path.exists()

    # Read datasets.jsonlines, convert to a list of Package objects
    packages = []
    with open(datasets_path) as f:
        for line in f:
            packages.append(Package(data=json.loads(line)))

    # Set of all paths to resource files
    resources = list(
        chain(*[map(d.joinpath, names) for d, _, names in resources_path.walk()])
    )

    print(f"Read {len(packages)} packages from {datasets_path}")
    print(f"{len(resources)} total resource files in {resources_path}")

    class STATE(Enum):
        """State of Resources associated with a Package."""

        NO_RESOURCES = auto()
        ALL_PRESENT_OR_URL = auto()
        ALL_MISSING = auto()
        MIXED = auto()

    # Sort packages into 3 lists according to the state of their resources
    packages1: dict[STATE, list[Package]] = {}
    for p in packages:
        present = []
        for r in p.resources:
            if r.has_local_file:
                local_path = r.local_path(resources_path)
                present.append(local_path.exists())
                resources.remove(local_path)
            else:
                present.append(True)
        if not len(present):
            key = STATE.NO_RESOURCES
        elif all(present):
            key = STATE.ALL_PRESENT_OR_URL
        elif not any(present):
            key = STATE.ALL_MISSING
        else:
            key = STATE.MIXED

        packages1.setdefault(key, [])
        packages1[key].append(p)

    for k, v in packages1.items():
        p = v[0]
        print(
            f"\n{len(v)} packages with state {k!r}",
            # "Example:",
            # p,
            # f"{len(p.resources)} total resources",
            sep="\n",
        )
        # for r in p.resources:
        #     _path = r.local_path(base_path)
        #     print(
        #         r,
        #         f"Expected path: {_path}",
        #         f"Path exists  : {_path.exists()}",
        #         json.dumps(r.asdict(), indent=2),
        #         sep="\n",
        #     )

    print(f"{len(resources)} resources not matched to packages")
