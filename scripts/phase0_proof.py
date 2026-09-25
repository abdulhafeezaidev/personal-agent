#!/usr/bin/env python3
"""
Personal Agent V1 - Phase 0 Environment Proof
Proves unattended interactive Windows desktop automation feasibility.

Sequence:
1. Start structured logging to console and logs/phase0_proof.log.
2. Record timestamp, username, process ID, and Windows session information.
3. Verify that an interactive desktop is available.
4. Launch Notepad.
5. Wait for the Notepad window using condition-based timeout.
6. Enter 'Personal Agent Phase 0 Verification'.
7. Verify that the expected Notepad window/process remains available.
8. Close Notepad cleanly without leaving an unsaved document.
9. Record PASS/FAIL in the log.
10. Exit with an appropriate process exit code.
"""

import sys
import os
import time
import subprocess
import logging
from datetime import datetime, timezone
import ctypes
from ctypes import wintypes

# Win32 API setup
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Constants
DESKTOP_SWITCHDESKTOP = 0x0100
SW_SHOW = 5
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_CLOSE = 0x0010
WM_CHAR = 0x0102

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)


def setup_logger(log_path: str) -> logging.Logger:
    """Set up structured logger writing to both file and stdout."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger = logging.getLogger("Phase0Proof")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_session_info() -> dict:
    """Gather Windows session and user metadata."""
    pid = kernel32.GetCurrentProcessId()
    session_id = wintypes.DWORD()
    kernel32.ProcessIdToSessionId(pid, ctypes.byref(session_id))
    user_name = os.environ.get("USERNAME", "unknown")
    domain_name = os.environ.get("USERDOMAIN", "unknown")

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "username": f"{domain_name}\\{user_name}",
        "process_id": pid,
        "session_id": session_id.value,
    }


def verify_interactive_desktop(logger: logging.Logger) -> bool:
    """
    Verify whether an active, accessible interactive desktop is available.
    Fails if session is locked, non-interactive, or cannot switch desktops.
    """
    logger.info("Verifying interactive desktop availability...")

    # Check input desktop access
    hdesk = user32.OpenInputDesktop(0, False, DESKTOP_SWITCHDESKTOP)
    if not hdesk:
        err = kernel32.GetLastError()
        logger.error(
            f"Failed to open input desktop. Win32 Error Code: {err} "
            "(Desktop is locked, running in non-interactive Session 0, or disconnected)."
        )
        return False

    user32.CloseDesktop(hdesk)

    desktop_hwnd = user32.GetDesktopWindow()
    if not desktop_hwnd:
        logger.error("GetDesktopWindow returned NULL handle.")
        return False

    logger.info(f"Interactive desktop confirmed available (Desktop HWND: {desktop_hwnd}).")
    return True


def find_notepad_window() -> tuple[int, int]:
    """
    Find top-level Notepad window handle and process ID.
    Returns (hwnd, pid) or (0, 0) if not found.
    """
    found_hwnd = 0
    found_pid = 0

    def enum_cb(hwnd, extra):
        nonlocal found_hwnd, found_pid
        if user32.IsWindowVisible(hwnd):
            class_buff = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buff, 256)
            if class_buff.value == "Notepad":
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                found_hwnd = hwnd
                found_pid = pid.value
                return False
        return True

    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return found_hwnd, found_pid


def find_edit_control(parent_hwnd: int) -> int:
    """Find the text edit control handle inside Notepad."""
    found_edit = 0

    def enum_child_cb(hwnd, extra):
        nonlocal found_edit
        class_buff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buff, 256)
        # Windows 11 uses RichEditD2DPT; classic Windows uses Edit
        if class_buff.value in ("RichEditD2DPT", "Edit"):
            found_edit = hwnd
            return False
        return True

    user32.EnumChildWindows(parent_hwnd, WNDENUMPROC(enum_child_cb), 0)
    return found_edit


def wait_for_condition(predicate, timeout: float = 15.0, interval: float = 0.2):
    """Wait for condition-based predicate to return truthy value."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = predicate()
        if result:
            return result
        time.sleep(interval)
    return None


def run_phase0_proof() -> int:
    """Execute Phase 0 proof sequence."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    log_file = os.path.join(project_root, "logs", "phase0_proof.log")

    logger = setup_logger(log_file)
    logger.info("=" * 60)
    logger.info("PHASE 0 ENVIRONMENT PROOF: EXECUTION START")
    logger.info("=" * 60)

    # 1. Record metadata
    meta = get_session_info()
    logger.info(f"Timestamp (UTC) : {meta['timestamp_utc']}")
    logger.info(f"User Context    : {meta['username']}")
    logger.info(f"Process ID      : {meta['process_id']}")
    logger.info(f"Session ID      : {meta['session_id']}")

    # 2. Check interactive desktop
    if not verify_interactive_desktop(logger):
        logger.error("RESULT: FAIL - Interactive desktop is NOT available.")
        logger.info("=" * 60)
        return 1

    proc = None
    target_hwnd = 0
    target_pid = 0
    edit_hwnd = 0
    test_string = "Personal Agent Phase 0 Verification"

    try:
        # 3. Launch Notepad
        logger.info("Launching notepad.exe...")
        proc = subprocess.Popen(["notepad.exe"])
        logger.info(f"Spawned notepad.exe launcher (Launcher PID: {proc.pid})")

        # 4. Wait for Notepad window using condition-based timeout
        logger.info("Waiting for Notepad top-level window to appear (timeout=15s)...")
        window_result = wait_for_condition(
            lambda: find_notepad_window() if find_notepad_window()[0] != 0 else None,
            timeout=15.0,
            interval=0.25
        )

        if not window_result:
            logger.error("RESULT: FAIL - Notepad window did not appear within timeout.")
            return 1

        target_hwnd, target_pid = window_result
        logger.info(f"Notepad window detected: HWND={target_hwnd}, PID={target_pid}")

        # Wait for edit control inside Notepad
        logger.info("Waiting for Notepad text edit control (timeout=10s)...")
        edit_result = wait_for_condition(
            lambda: find_edit_control(target_hwnd) if find_edit_control(target_hwnd) != 0 else None,
            timeout=10.0,
            interval=0.25
        )

        if not edit_result:
            logger.error("RESULT: FAIL - Text edit control not found inside Notepad window.")
            return 1

        edit_hwnd = edit_result
        logger.info(f"Notepad text edit control detected: HWND={edit_hwnd}")

        # 5. Bring window to front and enter text
        logger.info(f"Entering deterministic text: '{test_string}'...")
        user32.ShowWindow(target_hwnd, SW_SHOW)
        user32.SetForegroundWindow(target_hwnd)

        # Clear any prior text/tab buffer to guarantee clean state
        user32.SendMessageW(edit_hwnd, WM_SETTEXT, 0, "")
        time.sleep(0.1)

        # Enter text character-by-character via WM_CHAR
        for ch in test_string:
            user32.SendMessageW(edit_hwnd, WM_CHAR, ord(ch), 0)
            time.sleep(0.01)

        # 6. Verify that Notepad window/process remains available and text matches
        logger.info("Verifying window availability and content...")
        if not user32.IsWindow(target_hwnd):
            logger.error("RESULT: FAIL - Notepad window closed unexpectedly.")
            return 1

        # Read back content from edit control via WM_GETTEXT
        buff = ctypes.create_unicode_buffer(512)
        user32.SendMessageW(edit_hwnd, WM_GETTEXT, 512, buff)
        received_text = buff.value.strip()

        logger.info(f"Text read back from Notepad control: '{received_text}'")
        if received_text != test_string:
            logger.error(
                f"RESULT: FAIL - Content mismatch. Expected '{test_string}', got '{received_text}'"
            )
            return 1

        logger.info("Content verification successful: text received by Notepad matches expected string.")

        # 7. Close Notepad cleanly without leaving an unsaved document
        logger.info("Closing Notepad cleanly (resetting text and sending WM_CLOSE)...")
        # Clear content first so no 'Save Changes' dialog is triggered
        user32.SendMessageW(edit_hwnd, WM_SETTEXT, 0, "")
        time.sleep(0.1)

        # Send close message
        user32.SendMessageW(target_hwnd, WM_CLOSE, 0, 0)

        # Wait condition-based for window to close
        closed = wait_for_condition(
            lambda: True if not user32.IsWindow(target_hwnd) else None,
            timeout=5.0,
            interval=0.25
        )

        if closed:
            logger.info("Notepad window closed cleanly.")
        else:
            logger.warning("Notepad window did not close with WM_CLOSE; terminating process.")
            subprocess.run(["taskkill", "/F", "/PID", str(target_pid)], capture_output=True)

        logger.info("=" * 60)
        logger.info("RESULT: PASS - Phase 0 environment proof succeeded.")
        logger.info("=" * 60)
        return 0

    except Exception as ex:
        logger.exception(f"RESULT: FAIL - Unexpected exception during execution: {ex}")
        return 1

    finally:
        # Guarantee no lingering Notepad processes remain
        try:
            subprocess.run(["taskkill", "/F", "/IM", "Notepad.exe"], capture_output=True)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(run_phase0_proof())
