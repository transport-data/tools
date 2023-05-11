import os

import pytest


@pytest.fixture(scope="session")
def test_config(tmp_path_factory):
    name = "XDG_CONFIG_HOME"
    pre = os.environ.get(name)
    os.environ[name] = str(tmp_path_factory.mktemp("dot-config"))

    yield

    if pre is None:
        os.environ.pop(name)
    else:
        os.environ[name] = pre


usefixtures = test_config
