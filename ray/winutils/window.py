import ctypes
from ctypes import wintypes

SW_MINIMIZE = 6
WM_CLOSE = 0x0010

_user32 = ctypes.WinDLL("user32")
_user32.GetForegroundWindow.restype = wintypes.HWND
_user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
_user32.PostMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]


def minimize_active_window() -> bool:
    handle = _user32.GetForegroundWindow()
    if not handle:
        return False
    _user32.ShowWindow(handle, SW_MINIMIZE)
    return True


def close_active_window() -> bool:
    """Мягкое закрытие: программа сама спросит о сохранении, если нужно."""
    handle = _user32.GetForegroundWindow()
    if not handle:
        return False
    _user32.PostMessageW(handle, WM_CLOSE, 0, 0)
    return True


def lock_workstation() -> None:
    _user32.LockWorkStation()
