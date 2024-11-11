import pytest
from sdmx.model import v21

from transport_data.adb import convert, dataset_to_metadata_reports


@pytest.fixture(scope="session")
def ato_converted_data(tmp_store):
    """Converted ATO data and structures in the test data directory."""
    # 'Proper' method: repeat the conversion in the test data directory
    for part in ("ACC", "APH", "CLC", "INF", "MIS", "RSA", "SEC", "TAS"):
        convert(part)

    # # 'Fast' method: mirror the files from the user's directory
    # from shutil import copyfile

    # from transport_data import Config

    # source_dir = Config().data_path.joinpath("local")
    # dest_dir = tmp_store.store["local"].path

    # def predicate(p: Path) -> bool:
    #     return "ADB:" in p.name

    # for p in filter(predicate, source_dir.iterdir()):
    #     copyfile(p, dest_dir.joinpath(p.name))


@pytest.fixture
def ato_any_dataset(ato_converted_data) -> "v21.DataSet":
    """One (any) ATO data set."""
    from transport_data import STORE

    key = STORE.list(v21.DataSet, maintainer="ADB")[0]
    return STORE.get(key)


def test_convert0(ato_converted_data):
    """Test that :func:`.adb.convert` works for certain parts."""
    # Nothing in particular: simply request the fixture that generates the parts
    # TODO Add assertions about the numbers of data structures and sets converted


@pytest.mark.parametrize(
    "part",
    (pytest.param("POL", marks=pytest.mark.xfail(reason="File format differs")),),
)
def test_convert1(part):
    """Test other `part`s that need particular marks."""
    convert(part)


@pytest.mark.usefixtures("ato_converted_data")
def test_dataset_to_metadata_reports():
    from transport_data import STORE
    from transport_data.org.metadata import get_msd

    # Retrieve one particular converted data set
    datasets = filter(
        lambda k: "TAS-VEP-001" in k, STORE.list(v21.DataSet, maintainer="ADB")
    )
    ds = STORE.get(next(datasets))

    # Conversion works
    result = dataset_to_metadata_reports(ds, get_msd())

    # Multiple metadata reports are generated
    assert 10 == len(result)
