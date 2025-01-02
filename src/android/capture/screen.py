from typing import Union
import numpy as np
import win32con
import win32ui
import win32gui
from src.android.windows.hwnd import search_hwnd, search_mumu
from .base import Capturer
from src.utils.image import ImageExpander


class ScreenCapturer(Capturer):
    def __init__(self, x1, y1, w, h, hwnd: Union[int, str, None] = None, post_address=None):
        self.x1 = x1
        self.y1 = y1
        self.w = w
        self.h = h
        if hwnd is not None:
            if isinstance(hwnd, str):
                self.hwnd = int(hwnd, 16)
            elif isinstance(hwnd, int):
                self.hwnd = hwnd
        else:
            self.hwnd = search_mumu()
        print("获取句柄", self.hwnd)
        assert self.hwnd is not None, "如果不是使用Mumu模拟器，请自行指定句柄"
        self.post_address = post_address

        self.init_env()

    @classmethod
    def from_image_expander(cls, image_expander: ImageExpander, hwnd=None):
        cut_config = image_expander.get_cut_config()
        x1 = cut_config["x"]
        y1 = cut_config["y"]
        w = cut_config["w"]
        h = cut_config["h"]

        return cls(x1, y1, w, h, hwnd, image_expander.reshape)

    def capture(self):
        self.neicunDC.BitBlt((0, 0), (self.w, self.h), self.mfcDC, (self.x1, self.y1), win32con.SRCCOPY)
        signedIntsArray = self.savebitmap.GetBitmapBits(True)
        im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
        im_opencv.shape = (self.h, self.w, 4)
        im_opencv = im_opencv[..., :-1]  # 转为3通道 由于是索引的方式，注意一下内存问题
        if self.post_address:
            im_opencv = self.post_address(im_opencv)
        return im_opencv

    def init_env(self):
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.neicunDC = self.mfcDC.CreateCompatibleDC()
        self.savebitmap = win32ui.CreateBitmap()
        self.savebitmap.CreateCompatibleBitmap(self.mfcDC, self.w, self.h) # 开辟内存
        self.neicunDC.SelectObject(self.savebitmap) # 设定截图存储对象

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
