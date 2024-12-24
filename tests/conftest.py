import shutil
from pathlib import Path

import pytest

from tests.utils import generate_name

CHROMA_TEST_DIR = Path("/tmp/chroma-test")


def pytest_configure():
    print("Global setup")
    CHROMA_TEST_DIR.mkdir(parents=True, exist_ok=True)


def pytest_unconfigure():
    print("Global teardown")
    shutil.rmtree(CHROMA_TEST_DIR)

@pytest.fixture
def fixtures() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def global_setup_teardown():
    # Setup
    tmpdir = CHROMA_TEST_DIR / generate_name()
    tmpdir.mkdir(parents=True)

    # Test execution
    yield tmpdir

    # Teardown
    shutil.rmtree(tmpdir)
