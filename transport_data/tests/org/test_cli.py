from pathlib import Path

import pytest

from transport_data.testing import CliRunner


@pytest.mark.parametrize(
    "args, exit_code, stem",
    (
        (["--format=png", "https://example.com"], 0, "example-com"),
        (["--format=svg", "https://example.com"], 0, "example-com"),
        (["--format=foo", "https://example.com"], 2, ""),
        (["--format=png", "https://example.com/foo"], 0, "example-com-foo"),
        (["--format=png", "https://example.com/foo?bar=baz"], 0, "example-com-3098d"),
    ),
)
def test_qr(
    tmp_path: Path, tdc_cli: CliRunner, args: list[str], exit_code: int, stem: str
) -> None:
    with tdc_cli.isolated_filesystem(tmp_path):
        result = tdc_cli.invoke(["org", "qr"] + args)

    assert exit_code == result.exit_code

    if exit_code:
        return  # No further checks if the invocation is expected to fail

    # Temporary directory created by CliRunner
    dir = next(tmp_path.iterdir())

    # 1 file(s) created
    files = list(dir.iterdir())
    assert 1 == len(files)

    # Name of created file
    file = files[0]
    assert f"qr-{stem}" == file.stem
    assert "." + args[0][-3:] == file.suffix
