# hid_tests/tests/test_hash.py
from __future__ import annotations
import time
from pathlib import Path
from typing import Dict
import pytest
import hash_wrapper
import ctypes

from hid_tests.src.utils import _wait_done


@pytest.mark.functional
class TestHashFiles:

    def setup_method(self):
        self.samples_dir = Path(__file__).parent.parent / "data" / "samples" / "positive"
        if not self.samples_dir.exists():
            raise FileNotFoundError(f"Test data directory not found: {self.samples_dir}")
        self.invalid_op_id = 999999

    def test_init_library_success(self):
        result = None
        try:
            hash_wrapper.init_library()
            result = "ok"
        finally:
            hash_wrapper.terminate_library()
        assert result == "ok"

    def test_terminate_library_success(self):
        hash_wrapper.init_library()
        try:
            hash_wrapper.terminate_library()
        except RuntimeError:
            pytest.fail("terminate_library() should not fail after init")

    def test_terminate_without_init(self):
        with pytest.raises(RuntimeError) as exc_info:
            hash_wrapper.terminate_library()
        assert "hashterminate failed, error code 7" in str(exc_info.value).lower()

    def test_start_hashing_success(self, tmp_path):
        (tmp_path / "file1.txt").write_text("Hello hash")
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(tmp_path))
            assert isinstance(op_id, int)
            assert op_id > 0
            assert _wait_done(op_id), "Hashing did not complete in time"
        finally:
            hash_wrapper.terminate_library()

    @pytest.mark.skip(reason="Known bug id_hash_005, it's crashes the whole test run")
    @pytest.mark.xfail(reason="Known bug id_hash_005: HashDirectory crashes when path is invalid")
    def test_start_hashing_invalid_path(self):
        hash_wrapper.init_library()
        try:
            with pytest.raises(RuntimeError) as exc_info:
                hash_wrapper.start_hashing("/non/existing/path")
            assert "hashdirectory failed" in str(exc_info.value).lower()
        finally:
            hash_wrapper.terminate_library()

    @pytest.mark.xfail(reason="Known bug id_hash_001: HashReadNextLogLine returns code 1 instead of code 4")
    def test_read_log_line(self):
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(self.samples_dir))
            _wait_done(op_id, timeout_s=10)

            lines = []
            while True:
                line = hash_wrapper.read_log_line()
                if line is None:
                    break
                print(f"[DEBUG] Log line: {line}")
                lines.append(line)

            assert len(lines) > 0, "No log lines read"
            for line in lines:
                assert ":" in line, f"Unexpected log format: {line}"
        finally:
            hash_wrapper.terminate_library()

    def test_get_status_during_and_after(self):
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(self.samples_dir))

            running = hash_wrapper.get_status(op_id)
            assert isinstance(running, bool)
            assert running is True

            _wait_done(op_id, timeout_s=10)

            running = hash_wrapper.get_status(op_id)
            assert running is False
        finally:
            hash_wrapper.terminate_library()

    @pytest.mark.xfail(reason="Known bug id_hash_002: HashStatus silently ignores invalid op_id")
    def test_get_status_invalid_op_id(self):
        hash_wrapper.init_library()
        try:
            with pytest.raises(RuntimeError) as exc_info:
                hash_wrapper.get_status(self.invalid_op_id)
            assert "status failed" in str(exc_info.value).lower()
        finally:
            hash_wrapper.terminate_library()

    @pytest.mark.skip(reason="Known bug id_hash_003: HashStop has no effect on active operation")
    @pytest.mark.timeout(10)
    def test_stop_running_operation(self):
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(self.samples_dir))
            print(f"[DEBUG] Started op_id = {op_id}")
            time.sleep(0.1)
            print(f"[DEBUG] Stopping op_id = {op_id}")
            hash_wrapper.stop_operation(op_id)
            done = _wait_done(op_id, timeout_s=5)
            print(f"[DEBUG] Done = {done}")
            assert done, "Hashing did not stop after calling stop_operation()"
        finally:
            hash_wrapper.terminate_library()

    def test_stop_invalid_op_id(self):
        """
        # Need to clarify the correctness of behaviour - I use an invalid OP and test pass
        Not sure if it's a bug or "feature".
        """
        hash_wrapper.init_library()
        try:
            with pytest.raises(RuntimeError) as exc_info:
                hash_wrapper.stop_operation(self.invalid_op_id)
            assert "stop failed" in str(exc_info.value).lower()
        finally:
            hash_wrapper.terminate_library()

    def test_stop_after_completion(self):
        """
        What is really expected behavior if we try to stop completed operation?
        """
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(self.samples_dir))
            _wait_done(op_id, timeout_s=10)
            try:
                hash_wrapper.stop_operation(op_id)
            except RuntimeError as e:
                print(f"[WARN] stop after complete raised: {e}")
        finally:
            hash_wrapper.terminate_library()

    def test_free_memory_manual(self):
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(self.samples_dir))
            _wait_done(op_id, timeout_s=10)

            raw_ptr = ctypes.c_void_p()
            err = hash_wrapper.lib.HashReadNextLogLine(ctypes.byref(raw_ptr))
            assert err == hash_wrapper.HASH_ERROR_OK
            assert raw_ptr.value is not None

            hash_wrapper.free_memory(raw_ptr)
        finally:
            hash_wrapper.terminate_library()

    @pytest.mark.xfail(reason="Known bug id_hash_004: Duplicate log lines from read_log_line()")
    def test_hashes_generated_for_all_files(self):
        hash_wrapper.init_library()
        try:
            op_id = hash_wrapper.start_hashing(str(self.samples_dir))
            _wait_done(op_id, timeout_s=10)

            lines = []
            while True:
                try:
                    line = hash_wrapper.read_log_line()
                except RuntimeError as e:
                    if "error code 1" in str(e).lower():
                        break
                    raise
                if line is None:
                    break
                lines.append(line)

            expected_files = sorted(f.resolve() for f in self.samples_dir.iterdir() if f.is_file())
            found_files = sorted(Path(line.split()[1]).resolve() for line in lines)

            assert len(found_files) == len(expected_files), (
                f"Expected {len(expected_files)} hashes, but got {len(found_files)}"
            )

            assert set(found_files) == set(expected_files), (
                f"Mismatch between expected and found files:\nExpected: {expected_files}\nFound: {found_files}"
            )

        finally:
            hash_wrapper.terminate_library()
