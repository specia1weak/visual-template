from typing import Union

import numpy as np
import win32con
import win32gui
import win32ui
from src.android.capture.base import Capturer
from src.android.windows.hwnd import search_mumu, WindowMonitor, DESKTOP_HWND, get_window_rect, DESKTOP_WIDTH, \
    DESKTOP_HEIGHT
from src.utils.image import ImageExpander

class DesktopCapturer(Capturer):
    def __init__(self, hwnd: Union[int, str, None] = None, post_address=None):
        if hwnd is not None:
            if isinstance(hwnd, str):
                self.hwnd = int(hwnd, 16)
            elif isinstance(hwnd, int):
                self.hwnd = hwnd
        else:
            self.hwnd = search_mumu()
        print("获取句柄", self.hwnd)
        assert self.hwnd is not None, "如果不是使用Mumu模拟器，请自行指定句柄"
        self.window_monitor = WindowMonitor(self.hwnd)
        self.post_address = post_address
        self.x1, self.y1, self.x2, self.y2 = (0,) * 4
        self.init_env()
        self.update_capture_rect()

    @property
    def w(self):
        return self.x2 - self.x1

    @property
    def h(self):
        return self.y2 - self.y1

    def update_capture_rect(self):
        rect = self.window_monitor.update_window_rect()
        if rect != (self.x1, self.y1, self.x2, self.y2):
            self.x1, self.y1, self.x2, self.y2 = rect

    @classmethod
    def from_image_expander(cls, image_expander: ImageExpander, hwnd):
        return cls(hwnd, image_expander.reshape)

    def capture(self):
        self.update_capture_rect()
        self.neicunDC.BitBlt((0, 0), (DESKTOP_WIDTH, DESKTOP_HEIGHT), self.mfcDC, (0, 0), win32con.SRCCOPY)
        signedIntsArray = self.savebitmap.GetBitmapBits(True)
        im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
        im_opencv.shape = (DESKTOP_HEIGHT, DESKTOP_WIDTH, 4)
        im_opencv = im_opencv[..., :-1][self.y1: self.y2, self.x1: self.x2]  # 转为3通道 由于是索引的方式，注意一下内存问题
        if self.post_address:
            im_opencv = self.post_address(im_opencv)
        return im_opencv

    def init_env(self):
        self.hwndDC = win32gui.GetWindowDC(DESKTOP_HWND)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.neicunDC = self.mfcDC.CreateCompatibleDC()
        self.savebitmap = win32ui.CreateBitmap()
        self.savebitmap.CreateCompatibleBitmap(self.mfcDC, DESKTOP_WIDTH, DESKTOP_HEIGHT)  # 开辟内存
        self.neicunDC.SelectObject(self.savebitmap)  # 设定截图存储对象

    def clear(self):
        self.mfcDC.DeleteDC()
        self.neicunDC.DeleteDC()
        win32gui.DeleteObject(self.savebitmap.GetHandle())
        win32gui.ReleaseDC(self.hwndDC, self.hwndDC)

    def reset(self):
        self.clear()
        self.init_env()

    def __del__(self):
        self.clear()
