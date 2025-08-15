import tempfile
import time

import allure
import hash_wrapper as hw
import pytest
from allure_commons.types import AttachmentType


@allure.epic("Hash Library")
@allure.feature("Smoke")
@allure.story("Library load & minimal call sequence")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.smoke
def test_hash_wrapper_load_and_init():
    """
    Smoke test with Allure steps:
    - Verify wrapper API surface
    - Start hashing on a safe empty dir
    - Short status check
    - Attempt to read a log line (tolerate empty/general)
    - Stop operation to avoid hangs
    """

    with allure.step("Verify wrapper functions are present and callable"):
        required = [
            "init_library",
            "terminate_library",
            "start_hashing",
            "read_log_line",
            "get_status",
            "stop_operation",
            "free_memory",
        ]
        missing = [f for f in required if not hasattr(hw, f)]
        assert not missing, f"Missing functions: {missing}"
        for name in required:
            assert callable(getattr(hw, name)), f"{name} is not callable"

    with tempfile.TemporaryDirectory() as tmpdir:
        allure.attach(
            tmpdir, name="Temp directory", attachment_type=AttachmentType.TEXT
        )

        with allure.step("Start hashing on an empty directory"):
            op_id = hw.start_hashing(tmpdir)
            allure.attach(
                str(op_id), name="Operation ID", attachment_type=AttachmentType.TEXT
            )
            assert isinstance(op_id, int)

        with allure.step("Short delay to let the worker start"):
            time.sleep(0.1)

        with allure.step("Check operation status (boolean)"):
            running = hw.get_status(op_id)
            allure.attach(
                str(running), name="Running flag", attachment_type=AttachmentType.TEXT
            )
            assert isinstance(running, bool)

        with allure.step("Try to read next log line (empty/general allowed)"):
            try:
                line = hw.read_log_line()
                allure.attach(
                    str(line), name="Log line", attachment_type=AttachmentType.TEXT
                )
                assert line is None or isinstance(line, str)
            except RuntimeError as e:
                # Accept general/empty-log errors in smoke
                allure.attach(
                    str(e),
                    name="read_log_line error",
                    attachment_type=AttachmentType.TEXT,
                )
                assert any(s in str(e) for s in ("error code 1", "error code 4")), str(
                    e
                )

        with allure.step("Stop operation to ensure clean teardown"):
            hw.stop_operation(op_id)
