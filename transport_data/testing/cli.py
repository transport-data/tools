from typing import TYPE_CHECKING

import click

from transport_data.org.ckan import instance_option

if TYPE_CHECKING:
    from transport_data.util.ckan import Client


@click.group("test")
def main():
    """Utilities for testing and development."""


@main.command(params=[instance_option])
def wipe(instance: "Client"):  # pragma: no cover
    """Remove all packages in the CKAN test organization.

    This requires a configured API token with permissions to delete packages.
    """
    from transport_data.testing import CKAN_UUID

    client = instance

    result = client.organization_show(
        id=CKAN_UUID[f"{client.id.upper()} org test"], include_datasets=True
    )
    packages = result.packages
    if not packages:
        print(f"{result!r} contains no packages; nothing to do")
        return

    print(f"Will delete {len(packages)} packages:")
    for i, p in enumerate(packages, start=1):
        print(f"{i:3d}. {p!r}")

    user_input = input("\nType 'yes' to confirm: ")

    if user_input != "yes":
        return

    deleted = []
    for p in packages:
        client.package_delete(id=p.id)
        deleted.append(p)

    print(f"\nDeleted {len(packages)} packages")
