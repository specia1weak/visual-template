from abc import ABC, abstractmethod
from typing import Union, List

from src.android.capture import ScreenCapturer
from .constants import INIT_MODE
from .components.factory import DetectorFactory, OperationFactory, CommonInfoFactory
from .gui.utils import ScreenShotCropper
from .gui.applications import TemplateMatchConfigUI, CommonInfoConfigUI
from .components.comptype import OperationType, DetectorType
from .components.operations import TapOperation, TemplateOperation
from ..android.adb import KeyEvent
from src.utils.singleton import Singleton
from src.android.windows.hwnd import get_window_rect
from ..android.windows.hwnd import search_mumu

TEMPLATES_BASE_DIR = "data/templates_matching/"
TEMPLATES_IMAGE_DIR = "templates"
TEMPLATES_CONFIG_DIR = "configs"



import json
import os.path as osp
import os


# matching/resolution/game/configs/mode.json 或者 matching/resolution/game/configs/groups/mode.json
# matching/resolution/game/templates/mode/1.jpg

class TemplateConfigGenerator:
    def __init__(self, game: str, hwnd, mode, subdir=None):
        self.game = game
        rect = get_window_rect(hwnd)
        x1, y1, x2, y2 = rect
        self.width = x2 - x1
        self.height = y2 - y1
        self.cropper = ScreenShotCropper()
        self.mode = mode

        self.full_screen_capturer = ScreenCapturer(0, 0, self.width, self.height, hwnd)  # 全截屏
        # 分辨率 等 文件路径
        self.resolution = f"{self.width}x{self.height}"
        def create_dir(dir):
            if not osp.exists(dir):
                os.makedirs(dir)
                print(f"路径 '{dir}' 新创建。")
            else:
                print(f"路径 '{dir}' 已存在。")

        # 第一个-存放图片的路径是否存在  and 第二个-存放json的路径是否存在
        self.imgs_dir = osp.join(TEMPLATES_BASE_DIR, self.resolution, self.game, TEMPLATES_IMAGE_DIR)
        self.json_dir = osp.join(TEMPLATES_BASE_DIR, self.resolution, self.game, TEMPLATES_CONFIG_DIR)
        if subdir is not None:
            self.imgs_dir = osp.join(self.imgs_dir, subdir)
            self.json_dir = osp.join(self.json_dir, subdir)
        self.imgs_dir = osp.join(self.imgs_dir, self.mode)  # 图片和json文件是多对一，应该额外多一个文件夹
        self.json_file_name = f"{self.resolution}-{mode}.json"
        create_dir(self.imgs_dir)
        create_dir(self.json_dir)
        # 目标json文件是否存在
        self.json_file_path = osp.join(self.json_dir, self.json_file_name)
        if not osp.exists(self.json_file_path):
            with open(self.json_file_path, "w", encoding="utf8") as f:
                init_mode = {
                    "mode_name": mode,
                    "init_activated": True,
                    "templates": {}
                }
                json.dump(init_mode, f)
        self.cropper.set_save_dir(self.imgs_dir)

    def save2json(self, templates_config):
        print(templates_config)
        old_state_dict = json.load(open(self.json_file_path, 'r', encoding='utf8'))
        old_state_dict["templates"].update(templates_config)
        json.dump(old_state_dict, open(self.json_file_path, 'w', encoding='utf8'), indent=4, ensure_ascii=False)

    def shot_and_config(self, detector: DetectorType, operations: List[OperationType]):
        full_screen_shot = self.full_screen_capturer.capture()
        self.cropper.reset_img(full_screen_shot)
        # 检测头
        detector_config = DetectorFactory.generate_detector(self.cropper, detector)
        if detector_config is None:
            return None
        # 通用信息
        common_info = CommonInfoFactory.generate_common_info()
        if common_info is None:
            return None
        # 操作
        operation_configs = []
        for operation_type in operations:
            operation_config = OperationFactory.generate_operation(self.cropper, operation_type)
            if operation_config is None:
                return None
            operation_configs.append(operation_config)
        # template_config 整体
        """
        <template_name>: {
            "common_info" : {}
            "detector": {}
            "operations": [{}, {}]
        }
        """
        template_config = {
            detector_config.get("kwargs").get("template_name"): {
                "common_info": common_info,
                "detector": detector_config,
                "operations": [operation_config for operation_config in operation_configs]
            }
        }
        self.save2json(template_config)
