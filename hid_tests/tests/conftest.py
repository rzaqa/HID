import sys
from pathlib import Path

import hash_wrapper as hw
import pytest

# ---- Import path setup ----
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(scope="session", autouse=True)
def init_hash_library():
    """
    Initialize the hash library once before all tests,
    and terminate it after all tests complete.
    """
    hw.init_library()
    yield
    hw.terminate_library()
