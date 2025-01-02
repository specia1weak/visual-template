"""新的识别类
1.
识别种类 FixedRegion
识别结果 是否大于阈值

2.
识别种类 Exist
识别结果 是否存在大于阈值的

3.
识别种类 Global
识别结果 总是存在

4.
识别种类 Differ
识别结果 self.image 是否与上次不一样"""
from abc import ABC, abstractmethod
from typing import Tuple, Any, Union

import cv2
import numpy as np

from src.templates.gui.applications import TemplateMatchConfigUI
from src.templates.gui.base import ConfigUI
from src.templates.gui.utils import ScreenShotCropper
from src.templates.compare import compare_similarity_with_template, search_template, MatchMethod
from src.utils.binary import mean_binary_img, binary_bg_and_words_colors


class TemplateDetector(ABC):
    @classmethod
    @abstractmethod
    def generate(cls, cropper: ScreenShotCropper) -> Tuple:
        pass

    @abstractmethod
    def __init__(self):
        self.template_name = "Abstract"

    @abstractmethod
    def detect(self, full_screen_shot, show_detail) -> Tuple[bool, Union[None, dict]]:
        pass

def _print_similarity(template_name, similarity, threshold, detect_succeed):
    print(f"[{template_name}]: [{similarity: 2.f}/{threshold: 2.f}]. Detect: {detect_succeed}")

def _print_max_similarity_and_match_count(template_name, similarity_matrix, threshold, detect_count):
    print(f"[{template_name}]: [{np.max(similarity_matrix): 2.f}/{threshold: 2.f}]. Detect Count: {detect_count}")

def _print_no_detect(template_name):
    print(f"[{template_name}无需检测]. Detect: True")

class FixedRegionDetector(TemplateDetector):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        box_info = cropper.crop_box()
        if box_info is None:
            return
        (x1, y1, x2, y2), crop_image = box_info
        w, h = abs(x2 - x1), abs(y2 - y1)
        # 其他信息的读取
        config_ui = TemplateMatchConfigUI()
        kwargs = config_ui.query_config(check_valid=lambda d: d["template_name"])
        kwargs["threshold"] = float(kwargs["threshold"])
        template_name = kwargs.get("template_name")
        cropper.save(template_name)
        kwargs.update(
            {
                "region": [x1, y1, w, h],
                "template_image": cropper.get_save_path(template_name)
            }
        )
        return kwargs

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.template_name = kwargs.get("template_name")
        self.threshold = kwargs.get("threshold")
        self.match_method = kwargs.get("match_method")

        self.region = kwargs.get("region")
        self.x1, self.y1, self.w, self.h = self.region

        self.template_image_path = kwargs.get("template_image")
        self.template_image = cv2.imread(self.template_image_path)

    def detect(self, full_screen_shot, show_detail) -> Tuple[bool, Union[None, dict]]:
        region_image = full_screen_shot[self.y1: self.y1 + self.h, self.x1: self.x1 + self.w, ...]
        similarity = compare_similarity_with_template(region_image, self.template_image, self.match_method)
        detect_succeed = similarity >= self.threshold
        if show_detail:
            _print_similarity(self.template_name, similarity, self.threshold, detect_succeed)
        return detect_succeed, None


class RegionExistsDetector(TemplateDetector):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        print("被匹配模板")
        box_info = cropper.crop_box()
        if box_info is None: # 这个boxinfo没用，主要是他的截图需要保存下来
            return
        (template_x1, template_y1, template_x2, template_y2), template_img = box_info
        # 其他信息的读取
        class RegionExistConfigUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("template_name", "模板名称:")
                self.build_text_input("threshold", "检测阈值[0-1]", 0.94)
                self.build_combobox("match_method", "检测方案",
                                    MatchMethod.TM_CCOEFF_NORMED.name,
                                    tuple(MatchMethod.__members__.keys()))
                self.build_text_input("boxes_data_key", "检测结果key", "")

        config_ui = RegionExistConfigUI()
        kwargs = config_ui.query_config(check_valid=lambda d: d["template_name"])
        kwargs["threshold"] = float(kwargs["threshold"])
        template_name = kwargs.get("template_name")
        cropper.save(template_name) # 保存

        dx, dy = 0, 0
        boxes_data_key = kwargs.get("boxes_data_key")
        if boxes_data_key:
            print("设定xy的偏移(可以看做tap的最终位置)")
            tap_x, tap_y = cropper.select_tap_point()
            dx = tap_x - (template_x1 + template_x2) // 2
            dy = tap_y - (template_y1 + template_y2) // 2

        print("选取大区域")
        box_info = cropper.crop_box()
        (bg_x1, bg_y1, bg_x2, bg_y2), crop_image = box_info
        w, h = abs(bg_x2 - bg_x1), abs(bg_y2 - bg_y1)

        kwargs.update(
            {
                "background_region": [bg_x1, bg_y1, w, h],
                "template_image": cropper.get_save_path(template_name),
                "dx": dx,
                "dy": dy
            }
        )
        return kwargs

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.template_name = kwargs.get("template_name")
        self.threshold = kwargs.get("threshold")
        self.match_method = kwargs.get("match_method")

        self.background_region = kwargs.get("background_region")
        self.x1, self.y1, self.w, self.h = self.background_region
        self.dx, self.dy = kwargs.get("dx", 0), kwargs.get("dy", 0)

        self.template_image_path = kwargs.get("template_image")
        self.template_image = cv2.imread(self.template_image_path)

        self.boxes_data_key = kwargs.get("boxes_data_key")
        self.xyxy_boxes = None

    def detect(self, full_screen_shot, show_detail) -> Tuple[bool, Union[None, dict]]:
        background_region_image = full_screen_shot[self.y1: self.y1 + self.h, self.x1: self.x1 + self.w, ...]
        self.xyxy_boxes, similarity_matrix = search_template(self.template_image, background_region_image, self.match_method,
                                          self.threshold)
        ## xyxy_boxes 还要用 x1, y1矫正, 以及dx, dy
        self.xyxy_boxes = [(x1 + self.x1 + self.dx, y1 + self.y1 + self.dy,
                            x2 + self.x1 + self.dx, y2 + self.y1 + self.dy) for x1, y1, x2, y2 in self.xyxy_boxes]
        boxes_info = None
        if self.boxes_data_key:
            boxes_info = {
                self.boxes_data_key: self.xyxy_boxes
            }
        detect_succeed = len(self.xyxy_boxes) > 0
        if show_detail:
            _print_max_similarity_and_match_count(self.template_name, similarity_matrix, self.threshold, len(self.xyxy_boxes) > 0)
        return detect_succeed, boxes_info

class BinaryRegionExistsDetector(TemplateDetector):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        print("被匹配模板")
        box_info = cropper.crop_box()
        if box_info is None: # 这个boxinfo没用，主要是他的截图需要保存下来
            return
        (template_x1, template_y1, template_x2, template_y2), template_img = box_info
        _, bg_color, words_color = binary_bg_and_words_colors(template_img)
        # 其他信息的读取
        class RegionExistConfigUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("template_name", "模板名称:")
                self.build_text_input("threshold", "检测阈值[0-1]", 0.94)
                self.build_combobox("match_method", "检测方案",
                                    MatchMethod.TM_CCOEFF_NORMED.name,
                                    tuple(MatchMethod.__members__.keys()))
                self.build_text_input("boxes_data_key", "检测结果key", "")

        config_ui = RegionExistConfigUI()
        kwargs = config_ui.query_config(check_valid=lambda d: d["template_name"])
        kwargs["threshold"] = float(kwargs["threshold"])
        template_name = kwargs.get("template_name")
        cropper.save(template_name) # 保存

        dx, dy = 0, 0
        boxes_data_key = kwargs.get("boxes_data_key")
        if boxes_data_key:
            print("设定xy的偏移(可以看做tap的最终位置)")
            tap_x, tap_y = cropper.select_tap_point()
            dx = tap_x - (template_x1 + template_x2) // 2
            dy = tap_y - (template_y1 + template_y2) // 2

        print("选取大区域")
        box_info = cropper.crop_box()
        (bg_x1, bg_y1, bg_x2, bg_y2), crop_image = box_info
        w, h = abs(bg_x2 - bg_x1), abs(bg_y2 - bg_y1)
        kwargs.update(
            {
                "background_region": [bg_x1, bg_y1, w, h],
                "template_image": cropper.get_save_path(template_name),
                "dx": dx,
                "dy": dy,
                "bg_color": bg_color.tolist(),
                "words_color": words_color.tolist()
            }
        )
        return kwargs

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.template_name = kwargs.get("template_name")
        self.threshold = kwargs.get("threshold")
        self.match_method = kwargs.get("match_method")

        self.background_region = kwargs.get("background_region")
        self.x1, self.y1, self.w, self.h = self.background_region
        self.dx, self.dy = kwargs.get("dx", 0), kwargs.get("dy", 0)

        self.template_image_path = kwargs.get("template_image")
        self.template_image = cv2.imread(self.template_image_path)

        self.boxes_data_key = kwargs.get("boxes_data_key")
        self.bg_color = np.array(kwargs.get("bg_color"))
        self.words_color = np.array(kwargs.get("words_color"))
        self.xyxy_boxes = None

    def detect(self, full_screen_shot, show_detail) -> Tuple[bool, Union[None, dict]]:
        background_region_image = full_screen_shot[self.y1: self.y1 + self.h, self.x1: self.x1 + self.w, ...]
        binary_background_region_image = mean_binary_img(background_region_image, self.bg_color, self.words_color)
        binary_template_image = mean_binary_img(self.template_image, self.bg_color, self.words_color)
        self.xyxy_boxes, similarity_matrix = search_template(binary_template_image, binary_background_region_image,
                                                             self.match_method, self.threshold)
        ## xyxy_boxes 还要用 x1, y1矫正, 以及dx, dy
        self.xyxy_boxes = [(x1 + self.x1 + self.dx, y1 + self.y1 + self.dy,
                            x2 + self.x1 + self.dx, y2 + self.y1 + self.dy) for x1, y1, x2, y2 in self.xyxy_boxes]
        boxes_info = None
        if self.boxes_data_key:
            boxes_info = {
                self.boxes_data_key: self.xyxy_boxes
            }
        detect_succeed = len(self.xyxy_boxes) > 0
        if show_detail:
            _print_max_similarity_and_match_count(self.template_name, similarity_matrix, self.threshold, len(self.xyxy_boxes) > 0)
        return detect_succeed, boxes_info

class WithoutImageDetector(TemplateDetector):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        class TemplateNameConfigUI(ConfigUI):
            def create_widgets(self):
                self.build_text_input("template_name", "模板名称:")

        config_ui = TemplateNameConfigUI()
        kwargs = config_ui.query_config()
        return kwargs

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.template_name = kwargs.get("template_name")

    def detect(self, full_screen_shot, show_detail) -> Tuple[bool, Union[None, dict]]:
        if show_detail:
            _print_no_detect(self.template_name)
        return True, None


class FixedRegionDifferDetector(TemplateDetector):
    @classmethod
    def generate(cls, cropper: ScreenShotCropper):
        box_info = cropper.crop_box()
        if box_info is None:
            return
        (x1, y1, x2, y2), crop_image = box_info
        w, h = abs(x2 - x1), abs(y2 - y1)
        # 其他信息的读取
        config_ui = TemplateMatchConfigUI()
        kwargs = config_ui.query_config(check_valid=lambda d: d["template_name"])
        kwargs["threshold"] = float(kwargs["threshold"])
        kwargs.update(
            {
                "region": [x1, y1, w, h],
            }
        )
        return kwargs

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.template_name = kwargs.get("template_name")
        self.threshold = kwargs.get("threshold")
        self.match_method = kwargs.get("match_method")

        self.region = kwargs.get("region")
        self.x1, self.y1, self.w, self.h = self.region

        self.last_image = None

    def detect(self, full_screen_shot, show_detail) -> Tuple[bool, Union[None, dict]]:
        if self.last_image is None:
            return False, None
        region_image = full_screen_shot[self.y1: self.y1 + self.h, self.x1: self.x1 + self.w, ...]
        similarity = compare_similarity_with_template(region_image, self.last_image, self.match_method)
        self.last_image = region_image
        detect_succeed = similarity >= self.threshold
        if show_detail:
            _print_similarity("DifferDetector-" + self.template_name, similarity, self.threshold, detect_succeed)
        return detect_succeed, None
