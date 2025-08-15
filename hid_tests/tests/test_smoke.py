import allure
import pytest
from allure_commons.types import AttachmentType

import hid_tests.src.hash_wrapper as hw


@allure.epic("Hash Library")
@allure.feature("Smoke")
@allure.story("API surface check")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke  # type: ignore[misc]
def test_hash_wrapper_api_surface() -> None:
    """
    Smoke test: ensure all required functions exist and are callable in hash_wrapper.
    """
    required_functions = [
        "init_library",
        "terminate_library",
        "start_hashing",
        "read_log_line",
        "get_status",
        "stop_operation",
        "free_memory",
    ]

    missing = [f for f in required_functions if not hasattr(hw, f)]
    not_callable = [f for f in required_functions if not callable(getattr(hw, f, None))]

    allure.attach(
        str(required_functions),
        "Required functions",
        attachment_type=AttachmentType.TEXT,
    )
    allure.attach(
        str(missing), "Missing functions", attachment_type=AttachmentType.TEXT
    )
    allure.attach(
        str(not_callable), "Non-callable functions", attachment_type=AttachmentType.TEXT
    )

    assert not missing, f"Missing functions: {missing}"
    assert not not_callable, f"Non-callable functions: {not_callable}"
