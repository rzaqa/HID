# hid_tests/tests/test_end2end.py
from __future__ import annotations
import time
from pathlib import Path
from typing import Dict
import pytest
import hash_wrapper as hw

from hid_tests.src.utils import _wait_done, _drain_log_for_op




@pytest.mark.functional
def test_e2e_hardcoded_positive(hash_lib) -> None:
    base = Path("hid_tests/data/samples/positive").resolve()
    expected: Dict[str, Dict[str, object]] = {
        str(base / "a.txt"): {"md5": "F36B265220F5E88EDD57963A1109146"},
        str(base / "b.txt"): {"md5": "E2BB86331F1DE8CEF43E59D0D1E8FF51"},
    }

    op_id = hw.start_hashing(str(base))
    _ = _wait_done(op_id, timeout_s=5.0)
    # stop regardless to avoid blocking behaviors
    try:
        hw.stop_operation(op_id)
    except RuntimeError:
        pass

    actual = _drain_log_for_op(op_id, expect_count=len(expected), timeout_s=2.0)

    print("\n=== EXPECTED ===")
    for k, v in sorted({k: {'op_id': op_id, **v} for k, v in expected.items()}.items()):
        print(k, v)
    print("=== ACTUAL ===")
    for k, v in sorted(actual.items()):
        print(k, v)
    print("================\n")

    # compare file sets
    exp_with_op = {k: {'op_id': op_id, **v} for k, v in expected.items()}
    assert set(actual.keys()) == set(exp_with_op.keys())

    # compare md5s
    for k in exp_with_op:
        assert actual[k]['md5'] == exp_with_op[k]['md5'], f"{k}: {actual[k]['md5']} != {exp_with_op[k]['md5']}"
        assert actual[k]['op_id'] == op_id
