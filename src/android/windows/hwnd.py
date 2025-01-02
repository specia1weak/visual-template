from typing import Union

import win32gui

DESKTOP_HWND = 0
DESKTOP_WIDTH = 1920
DESKTOP_HEIGHT = 1200


def get_child_windows(parent):
    if not parent:
        return
    hwndChildList = []
    win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd), hwndChildList)
    return hwndChildList


def search_hwnd(parent_window, child_window=None):
    parent_handle = win32gui.FindWindow(None, parent_window)
    if parent_handle != 0 and child_window is not None:
        children = get_child_windows(parent_handle)
        for child in children:
            cls_name = win32gui.GetClassName(child)
            if cls_name == child_window:
                return child
    return parent_handle


def search_mumu(window_title="MuMu模拟器1"):
    return search_hwnd(window_title, "nemuwin")


def search_nox():
    return search_hwnd("夜神模拟器", "subWin")


def get_window_rect(hwnd: int):
    rect = win32gui.GetWindowRect(hwnd) # xyxy
    return rect


class WindowMonitor:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.curr_window_rect = None
        self.update_window_rect()

    def update_window_rect(self):
        rect = get_window_rect(self.hwnd)
        self.curr_window_rect = rect
        return rect
