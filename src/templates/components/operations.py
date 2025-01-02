import math
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

import cv2

from src.android.adb import adb_text_input, KeyEvent, adb_key_event
from src.android.capture import ScreenCapturer
from src.android.operators.base import Operator
from src.templates.gui.base import ConfigUI
from src.templates.gui.utils import ScreenShotCropper
from src.utils.number import ImageNumberSplitter


class TemplateOperation(ABC):
    @classmethod
    @abstractmethod
    def generate(cls, cropper: ScreenShotCropper):
        pass

    @abstractmethod
    def __init__(self, **params):
        pass

    @abstractmethod
    def execute(self, operator: Operator, dataset: dict):
        pass


"""
operations: [                    执行的操作，点、滑、截图、adb input等等
    {
        type: "tap"/"slide"/"adb_event"/"text"/"screen"
        params: {
            不同的操作类型有不同参数，包括点击区域等等
        }
    },
]
"""


## 绝对值单点
class TapOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        ret = cropper.select_tap_point()
        if not cropper.valid_shot():
            return
        tap_x, tap_y = ret
        # 获取坐标信息
        params = {
            "x": tap_x,
            "y": tap_y
        }
        return params

    def __init__(self, **params):
        self.x, self.y = params.get("x"), params.get("y")

    def execute(self, operator, dataset: dict):
        operator.tap((self.x, self.y))

## 拖动
class DragOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        ret = cropper.drag_arrow()
        # 输入名称
        if not cropper.valid_shot():
            return

        p1, p2 = ret
        x1, y1 = p1
        x2, y2 = p2
        # 获取坐标信息
        params = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        return params

    def __init__(self, **params):
        self.x1 = params.get("x1")
        self.y1 = params.get("y1")
        self.x2 = params.get("x2")
        self.y2 = params.get("y2")
        self.pixels_per_second = params.get("speed", 300)  # 300 像素每秒
        self.interval = 0.01  # 操作帧率 为100Hz

    def execute(self, operator, dataset: dict):
        # 10ms 结算一次移动
        operator.down([(self.x1, self.y1)], [0])
        dw, dh = self.x2 - self.x1, self.y2 - self.y1
        move_count = max(
            abs(math.ceil(dw / (self.pixels_per_second * self.interval))),
            abs(math.ceil(dh / (self.pixels_per_second * self.interval)))
        )
        dx = dw / move_count
        dy = dh / move_count
        for mc in range(1, move_count + 1):
            print([(math.floor(self.x1 + mc * dx), math.floor(self.y1 + mc * dy))])
            operator.move([(math.floor(self.x1 + mc * dx), math.floor(self.y1 + mc * dy))], 0)
            from src.utils.time import high_precision_sleep
            high_precision_sleep(self.interval)
        time.sleep(0.1)
        operator.up([0])


## adb input text
## 我希望不要写死，应该是从一个数据结构自动取数据
class ADBTextOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class DataSrcKeyUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("data_key", info="数据源key")

        data_src_key_ui = DataSrcKeyUI()
        params = data_src_key_ui.query_config()
        return params

    def __init__(self, **params):
        self.data_key = params.get("data_key")

    def execute(self, operator, dataset: dict):
        info = operator.get_info()
        device_id = info.get("device_id")
        text = dataset.get(self.data_key)
        adb_text_input(text, device_id=device_id)


## 这个应该可以写死
class ADBKeyEventOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class KeyEventUI(ConfigUI):
            def create_widgets(self):
                self.build_combobox("key_event", "adb按键", default="请选择",
                                    options=tuple(KeyEvent.__members__.keys()))

        key_event_ui = KeyEventUI()
        params = key_event_ui.query_config()
        return params

    def __init__(self, **params):
        key_event = params.get("key_event")
        self.key_event = KeyEvent.__dict__.get(key_event.upper())

    def execute(self, operator, dataset: dict):
        info = operator.get_info()
        device_id = info.get("device_id")
        adb_key_event(self.key_event, device_id=device_id)


class ScreenShotOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class SavePathUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("save_path_data_key", "截图保存路径data_key")

        save_path_ui = SavePathUI()
        params = save_path_ui.query_config()
        return params

    def __init__(self, **params):
        self.save_path_data_key = params.get("save_path_data_key")

    def execute(self, operator, dataset: dict):
        screen_capturer: ScreenCapturer = dataset.get("screen_capturer")
        image = screen_capturer.capture()
        save_path = dataset.get(self.save_path_data_key)
        cv2.imwrite(save_path, image)


class BoxesDataKeyTapOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class BoxesKeyUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("boxes_data_key", "detector的data_key")

        boxes_key_ui = BoxesKeyUI()
        params = boxes_key_ui.query_config()
        return params

    def __init__(self, **params):
        self.boxes_data_key = params.get("boxes_data_key")

    def execute(self, operator, dataset: dict):
        xyxy_boxes = dataset.get(self.boxes_data_key)
        for x1, y1, x2, y2 in xyxy_boxes:
            operator.tap(
                ((x1 + x2) // 2, (y1 + y2) // 2)
            )
            time.sleep(0.1)


class SleepOperation(TemplateOperation):

    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class SleepTimeUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("sleep_time", "sleep(s)", "1.0", float)

        sleep_time_ui = SleepTimeUI()
        params = sleep_time_ui.query_config()
        return params

    def __init__(self, **params):
        self.sleep_time = params.get("sleep_time")

    def execute(self, operator: Operator, dataset: dict):
        time.sleep(self.sleep_time)


class RecognizeNumberOperation(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        ret = cropper.crop_box()
        if ret is None:
            return None
        xyxy, _ = ret
        x1, y1, x2, y2 = xyxy
        class NumberKeyUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("number_key", "数字保存的data_key", "")

        number_key_ui = NumberKeyUI()
        params = number_key_ui.query_config()
        params.update({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })
        return params

    def __init__(self, **params):
        self.number_key = params.get("number_key")
        self.x1 = params.get("x1")
        self.y1 = params.get("y1")
        self.x2 = params.get("x2")
        self.y2 = params.get("y2")

    def execute(self, operator: Operator, dataset: dict):
        img_num_splitter: ImageNumberSplitter = ImageNumberSplitter()
        screen_capturer: ScreenCapturer = dataset.get("screen_capturer")
        image = screen_capturer.capture()
        region_image = image[self.y1: self.y2, self.x1: self.x2]
        numbers_info = img_num_splitter.split_numbers_boxes(region_image)
        dataset[self.number_key] = "".join(map(str, numbers_info["numbers"]))


"""
operations: [                    执行的操作，点、滑、截图、adb input等等
    {
        type: "tap"/"slide"/"adb_event"/"text"/"screen"
        params: {
            不同的操作类型有不同参数，包括点击区域等等
        }
    },
]
"""

