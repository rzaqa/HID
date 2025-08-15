import ctypes
import os
import platform
from ctypes import POINTER, byref, c_bool, c_char_p, c_size_t, c_uint32, c_void_p

# ----------------------------
# Error codes from hash.h
# ----------------------------
HASH_ERROR_OK = 0
HASH_ERROR_GENERAL = 1
HASH_ERROR_EXCEPTION = 2
HASH_ERROR_MEMORY = 3
HASH_ERROR_LOG_EMPTY = 4
HASH_ERROR_ARGUMENT_INVALID = 5
HASH_ERROR_ARGUMENT_NULL = 6
HASH_ERROR_NOT_INITIALIZED = 7
HASH_ERROR_ALREADY_INITIALIZED = 8


# ----------------------------
# Determine library path
# ----------------------------
def _get_library_path() -> str:
    """
    Determine the correct library path based on OS.

    Assumes the library is stored in:
    HID/lib/<platform>/
    """
    # Go up two levels: src/hash_wrapper.py → hid_tests → HID
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    lib_dir = os.path.join(base_dir, "lib")

    system_name = platform.system().lower()

    if system_name == "darwin":  # macOS
        lib_path = os.path.join(lib_dir, "mac", "libhash.dylib")
    elif system_name == "linux":
        lib_path = os.path.join(lib_dir, "linux", "libhash.so")
    elif system_name == "windows":
        lib_path = os.path.join(lib_dir, "win", "hash.dll")
    else:
        raise RuntimeError(f"Unsupported OS: {system_name}")

    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Library file not found: {lib_path}")

    return lib_path


LIB_PATH = _get_library_path()

# ----------------------------
# Load the library
# ----------------------------
lib = ctypes.CDLL(LIB_PATH)

# ----------------------------
# Function signatures
# ----------------------------
lib.HashInit.argtypes = []
lib.HashInit.restype = c_uint32

lib.HashTerminate.argtypes = []
lib.HashTerminate.restype = c_uint32

lib.HashDirectory.argtypes = [c_char_p, POINTER(c_size_t)]
lib.HashDirectory.restype = c_uint32

lib.HashReadNextLogLine.argtypes = [POINTER(c_char_p)]
lib.HashReadNextLogLine.restype = c_uint32

lib.HashStatus.argtypes = [c_size_t, POINTER(c_bool)]
lib.HashStatus.restype = c_uint32

lib.HashStop.argtypes = [c_size_t]
lib.HashStop.restype = c_uint32

lib.HashFree.argtypes = [c_void_p]
lib.HashFree.restype = None


# ----------------------------
# Python wrapper functions
# ----------------------------
def init_library():
    """Initialize the hash library."""
    err = lib.HashInit()
    if err != HASH_ERROR_OK:
        raise RuntimeError(f"HashInit failed, error code {err}")


def terminate_library():
    """Terminate the hash library."""
    err = lib.HashTerminate()
    if err != HASH_ERROR_OK:
        raise RuntimeError(f"HashTerminate failed, error code {err}")


def start_hashing(directory: str) -> int:
    """Start hashing all files in the given directory."""
    op_id = c_size_t()
    err = lib.HashDirectory(directory.encode("utf-8"), byref(op_id))
    if err != HASH_ERROR_OK:
        raise RuntimeError(f"HashDirectory failed, error code {err}")
    return op_id.value


def read_log_line() -> str | None:
    """Read the next log line, or None if the log is empty."""
    line_ptr = c_char_p()
    err = lib.HashReadNextLogLine(byref(line_ptr))
    if err == HASH_ERROR_LOG_EMPTY:
        return None
    if err != HASH_ERROR_OK:
        raise RuntimeError(f"HashReadNextLogLine failed, error code {err}")
    line = ctypes.string_at(line_ptr).decode("utf-8")
    free_memory(line_ptr)
    return line


def get_status(op_id: int) -> bool:
    """Check whether the given operation is still running."""
    running_flag = c_bool()
    err = lib.HashStatus(c_size_t(op_id), byref(running_flag))
    if err != HASH_ERROR_OK:
        raise RuntimeError(f"HashStatus failed, error code {err}")
    return running_flag.value


def stop_operation(op_id: int):
    """Stop the given hashing operation."""
    err = lib.HashStop(c_size_t(op_id))
    if err != HASH_ERROR_OK:
        raise RuntimeError(f"HashStop failed, error code {err}")


def free_memory(ptr):
    """Free memory allocated by the library."""
    if ptr:
        lib.HashFree(ptr)
