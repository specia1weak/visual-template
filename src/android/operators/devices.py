import json
import time

from ..pyminitouch import BlitzDevice
from ..pyminitouch.utils import connect_device, reconnect_device_if_connected
from .base import OperatorDevice

"""
为什么要分横竖屏？因为Mumu模拟器横屏的坐标逻辑是横着的竖屏
但是如果用Pyautogui的operator就不需要，因为他的坐标逻辑与句柄一致
"""


class PortraitMumuOperator(OperatorDevice):
    def __init__(self, device_id):
        self.device_id = device_id
        reconnect_device_if_connected(device_id)
        self.device = None
        self.width = None
        self.height = None
        self._init_connect()

    def _init_connect(self):
        self.device = BlitzDevice(self.device_id)
        self.width = int(self.device.connection.max_x)
        self.height = int(self.device.connection.max_y)

    def single(self, xys, fingers):
        self.device.swift_tap(xys, fingers, duration=0)

    def down(self, xys, fingers):
        """
        输入flick检测xn值
        等待适时机会，你可以调用flick_move 不同手指的移动目的地
        一定要与flick_up flick_move配套使用，并且根据lane id 指定手指
        """
        self.device.swift_press(xys, fingers)

    def move(self, xys, fingers):
        """
       各个手指的滑动目的地，目的地仍然用xn，yn表示
        """
        self.device.swift_move(xys, fingers)

    def up(self, fingers):
        """
        传入手指ids就行了, flick_up 后的一段时间不允许被按下
        """
        self.device.swift_release(fingers)

    def tap(self, xy):
        self.device.swift_tap(xy, 0, duration=100)

    def stop(self):
        self.device.stop()

    def get_info(self):
        return {
            "w": self.width,
            "h": self.height,
            "device_id": self.device_id,
            "device_type": "PortraitMumuOperator"
        }


class LandscapeMumuOperator(OperatorDevice):
    def __init__(self, device_id):
        self.device_id = device_id
        reconnect_device_if_connected(device_id)
        self.device = None
        self.width = None
        self.height = None
        self._init_connect()

    def _init_connect(self):
        self.device = BlitzDevice(self.device_id)
        self.width = int(self.device.connection.max_y)  # mumu模拟器的width是反的
        self.height = int(self.device.connection.max_x)

    def _xy_reverse(self, original_xy):
        old_x, old_y = original_xy
        new_x, new_y = self.height - old_y, old_x
        return new_x, new_y

    def _xys_reverse(self, original_xys):
        """
        :param original_xys: 原始xys
        :return: 为了适配mumu横屏的反转xys
        """
        reversed_xys = []
        for original_xy in original_xys:
            reversed_xy = self._xy_reverse(original_xy)  # self.height是我们看上去的height  old_y 是我们看上去的y
            reversed_xys.append(reversed_xy)
        return reversed_xys

    def single(self, xys, fingers):
        reversed_xys = self._xys_reverse(xys)
        self.device.swift_tap(reversed_xys, fingers, duration=0)

    def down(self, xys, fingers):
        """
        输入flick检测xn值
        等待适时机会，你可以调用flick_move 不同手指的移动目的地
        一定要与flick_up flick_move配套使用，并且根据lane id 指定手指
        """
        reversed_xys = self._xys_reverse(xys)
        self.device.swift_press(reversed_xys, fingers)

    def move(self, xys, fingers):
        """
       各个手指的滑动目的地，目的地仍然用xn，yn表示
        """
        reversed_xys = self._xys_reverse(xys)
        self.device.swift_move(reversed_xys, fingers)

    def up(self, fingers):
        """
        传入手指ids就行了, flick_up 后的一段时间不允许被按下
        """
        self.device.swift_release(fingers)

    def tap(self, xy):
        reversed_xy = self._xy_reverse(xy)
        self.device.swift_tap(reversed_xy, 0, duration=100)

    def stop(self):
        self.device.stop()

    def get_info(self):
        return {
            "w": self.width,
            "h": self.height,
            "device_id": self.device_id,
            "device_type": "LandscapeMumuOperator"
        }


class AutoMumuOperator:
    def __new__(cls, device_id, hwnd):
        from ..windows.hwnd import get_window_rect
        x1, y1, x2, y2 = get_window_rect(hwnd)
        width = x2 - x1
        height = y2 - y1
        if width >= height:
            return LandscapeMumuOperator(device_id)
        else:
            return PortraitMumuOperator(device_id)


from src.android.adb import adb_cmd
from src.android.adb.touchscreen import adb_down, adb_move, adb_up, adb_tap
class AdbOperator(OperatorDevice):

    def __init__(self, device_id):
        self.device_id = device_id
        size_str = adb_cmd(['shell', 'wm', 'size'], device_id=device_id)
        size_str = size_str.decode('utf-8').strip().replace("x", " ")
        self.width, self.height = map(int, size_str.split(" ")[-2:])
        self.last_position = None

    def single(self, xyns, fingers=None):
        self.tap(xyns[0])

    def down(self, xyns, fingers=None):
        adb_down(xyns[0], self.device_id)
        self.last_position = xyns[0]

    def up(self, fingers=None):
        if self.last_position is not None:
            adb_up(self.last_position, self.device_id)
        self.last_position = None

    def move(self, xyns, fingers=None):
        adb_move(xyns[0], self.device_id)
        self.last_position = xyns[0]

    def tap(self, xy):
        adb_tap(xy, self.device_id)
        self.last_position = None

    def stop(self):
        pass

    def get_info(self):
        return {
            "w": self.width,
            "h": self.height,
            "device_id": self.device_id,
            "device_type": "AdbOperator"
        }


import pyautogui as pg
pg.PAUSE = 0.

class PyautoguiOperator(OperatorDevice):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1

    @classmethod
    def from_hwnd(cls, hwnd):
        import win32gui
        x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
        return cls(x1, y1, x2, y2)

    def _add_bias(self, xy):
        x, y = xy
        return x + self.x1, y + self.y1

    def single(self, xys, fingers=None):
        x, y = self._add_bias(xys[0])
        pg.leftClick(x, y)

    def down(self, xys, fingers=None):
        x, y = self._add_bias(xys[0])
        pg.mouseDown(x, y)

    def up(self, fingers=None):
        pg.mouseUp()

    def move(self, xys, fingers=None):
        x, y = self._add_bias(xys[0])
        pg.moveTo(x, y)

    def tap(self, xy):
        x, y = self._add_bias(xy)
        pg.leftClick(x, y, duration=0.1)

    def stop(self):
        pass

    def get_info(self):
        return {
            "w": self.width,
            "h": self.height,
            "device_id": None,
            "device_type": "PyautoguiOperator"
        }


class NullOperator(OperatorDevice):
    def single(self, xyns, fingers):
        pass

    def down(self, xyns, fingers):
        pass

    def up(self, fingers):
        pass

    def move(self, xyns, fingers):
        pass

    def tap(self, xy):
        pass

    def stop(self):
        pass

    def get_info(self):
        pass
