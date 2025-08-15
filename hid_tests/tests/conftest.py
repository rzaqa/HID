import hash_wrapper as hw
import pytest


# I prepared a fixture for future tests. But it's not used anywhere
@pytest.fixture(scope="function")
def hash_lib():
    hw.init_library()
    yield
    try:
        hw.terminate_library()
    except RuntimeError as e:
        if "error code 7" in str(e):
            print("⚠️ Library already terminated, skipping")
        else:
            raise
