import math
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

import cv2

from src.android.adb import adb_text_input, KeyEvent, adb_key_event
from src.android.capture import ScreenCapturer
from src.android.capture.base import Capturer
from src.android.operators.base import Operator
from src.templates.compare import search_template, MatchMethod
from src.templates.gui.base import ConfigUI
from src.templates.gui.utils import ScreenShotCropper
from src.utils.number import ImageNumberSplitter
from src.utils.time import set_min_time


class TemplateOperation(ABC):
    @classmethod
    @abstractmethod
    def generate(cls, cropper: ScreenShotCropper):
        pass

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
        pass


"""
operations: [                    执行的操作，点、滑、截图、adb input等等
    {
        type: "tap"/"slide"/"adb_event"/"text"/"screen"
        kwargs: {
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
        kwargs = {
            "x": tap_x,
            "y": tap_y
        }
        return kwargs

    def __init__(self, **kwargs):
        self.x, self.y = kwargs.get("x"), kwargs.get("y")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
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
        class SpeedConfigUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("speed", "速度（像素/s）", default=300, post_address=int)

        kwargs = SpeedConfigUI().query_config()
        # 获取坐标信息
        kwargs.update({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })
        return kwargs

    def __init__(self, **kwargs):
        self.x1 = kwargs.get("x1")
        self.y1 = kwargs.get("y1")
        self.x2 = kwargs.get("x2")
        self.y2 = kwargs.get("y2")
        self.pixels_per_second = kwargs.get("speed", 300)  # 300 像素每秒
        self.interval = 0.01  # 操作帧率 为100Hz

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
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
        kwargs = data_src_key_ui.query_config()
        return kwargs

    def __init__(self, **kwargs):
        self.data_key = kwargs.get("data_key")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
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
        kwargs = key_event_ui.query_config()
        return kwargs

    def __init__(self, **kwargs):
        key_event = kwargs.get("key_event")
        self.key_event = KeyEvent.__dict__.get(key_event.upper())

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
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
        kwargs = save_path_ui.query_config()
        return kwargs

    def __init__(self, **kwargs):
        self.save_path_data_key = kwargs.get("save_path_data_key")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
        screen_capturer: ScreenCapturer = capturer
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
        kwargs = boxes_key_ui.query_config()
        return kwargs

    def __init__(self, **kwargs):
        self.boxes_data_key = kwargs.get("boxes_data_key")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
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
        kwargs = sleep_time_ui.query_config()
        return kwargs

    def __init__(self, **kwargs):
        self.sleep_time = kwargs.get("sleep_time")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
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
        kwargs = number_key_ui.query_config()
        kwargs.update({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })
        return kwargs

    def __init__(self, **kwargs):
        self.number_key = kwargs.get("number_key")
        self.x1 = kwargs.get("x1")
        self.y1 = kwargs.get("y1")
        self.x2 = kwargs.get("x2")
        self.y2 = kwargs.get("y2")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
        img_num_splitter: ImageNumberSplitter = ImageNumberSplitter()
        screen_capturer: ScreenCapturer = capturer
        image = screen_capturer.capture()
        region_image = image[self.y1: self.y2, self.x1: self.x2]
        numbers_info = img_num_splitter.split_numbers_boxes(region_image)
        dataset[self.number_key] = "".join(map(str, numbers_info["numbers"]))


# 你看不懂就对了, 虽然很乱，起码三个逻辑相近的函数紧靠一块
class RepeatDragTillRegionExists(TemplateOperation):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class SavePathUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("template_name", "被搜索图片的命名, 一定要出现在其他detector中的同名template", "")
                self.build_text_input("speed", "速度（像素/s）", default=300, post_address=int)
        save_path_ui = SavePathUI()
        kwargs = save_path_ui.query_config()
        template_name = kwargs["template_name"]
        search_target_path = cropper.get_save_path(template_name)
        print("截取小区域")
        ret = cropper.crop_box()
        if ret is None:
            return None
        region_xyxy, _ = ret
        rx1, ry1, rx2, ry2 = region_xyxy
        print("设定拖拽方向")
        p1, p2 = cropper.drag_arrow()
        px1, py1 = p1
        px2, py2 = p2
        kwargs.update({
            "rx1": rx1,
            "ry1": ry1,
            "rx2": rx2,
            "ry2": ry2,
            "search_target": search_target_path,
            "px1": px1,
            "py1": py1,
            "px2": px2,
            "py2": py2,
        })
        return kwargs

    def __init__(self, **kwargs):
        self.search_target_path = kwargs.get("search_target")
        self.template = cv2.imread(self.search_target_path)
        self.pixels_per_second = kwargs.get("speed", 300)  # 300 像素每秒
        self.interval = 0.01  # 操作帧率 为100Hz
        self.rx1 = kwargs.get("rx1")
        self.ry1 = kwargs.get("ry1")
        self.rx2 = kwargs.get("rx2")
        self.ry2 = kwargs.get("ry2")
        self.px1 = kwargs.get("px1")
        self.py1 = kwargs.get("py1")
        self.px2 = kwargs.get("px2")
        self.py2 = kwargs.get("py2")

    def execute(self, operator: Operator, capturer: Capturer, dataset: dict):
        screen_capturer: ScreenCapturer = capturer
        @set_min_time(self.interval)
        def check_exists():
            full_screen_shot = screen_capturer.capture()
            region_img = full_screen_shot[self.ry1: self.ry2, self.rx1: self.rx2]
            final_xyxy_boxes, sim_matrix = search_template(self.template, region_img, method=MatchMethod.TM_CCOEFF_NORMED)
            import numpy as np
            print(np.max(sim_matrix))
            print(len(final_xyxy_boxes))
            return len(final_xyxy_boxes)

        detect_exists = False

        while not detect_exists:
            time.sleep(0.1)
            # 10ms 结算一次移动
            operator.down([(self.px1, self.py1)], [0])
            dw, dh = self.px2 - self.px1, self.py2 - self.py1
            move_count = max(
                abs(math.ceil(dw / (self.pixels_per_second * self.interval))),
                abs(math.ceil(dh / (self.pixels_per_second * self.interval)))
            )
            dx = dw / move_count
            dy = dh / move_count
            for mc in range(1, move_count + 1):
                print([(math.floor(self.px1 + mc * dx), math.floor(self.py1 + mc * dy))])
                operator.move([(math.floor(self.px1 + mc * dx), math.floor(self.py1 + mc * dy))], 0)
                detect_count = check_exists()
                if detect_count:
                    detect_exists = True
                    break
            operator.up([0])

"""
operations: [                    执行的操作，点、滑、截图、adb input等等
    {
        type: "tap"/"slide"/"adb_event"/"text"/"screen"
        kwargs: {
            不同的操作类型有不同参数，包括点击区域等等
        }
    },
]
"""

