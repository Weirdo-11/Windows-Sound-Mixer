import ctypes
import sys

from PySide6.QtWidgets import QWidget

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_SYSTEMBACKDROP_TYPE = 38

DWMWCP_ROUND = 2
DWMSBT_TRANSIENTWINDOW = 3


def apply_acrylic_effect(window: QWidget) -> None:
    if sys.platform != "win32":
        return

    try:
        dwmapi = ctypes.windll.dwmapi
        hwnd = int(window.winId())

        for attribute, value in (
            (DWMWA_USE_IMMERSIVE_DARK_MODE, 1),
            (DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND),
            (DWMWA_SYSTEMBACKDROP_TYPE, DWMSBT_TRANSIENTWINDOW),
        ):
            c_value = ctypes.c_int(value)
            dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(c_value), ctypes.sizeof(c_value))
    except OSError:
        pass
