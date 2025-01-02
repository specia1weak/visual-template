import json
import time
from typing import List, Dict, Union, Set

from .template import TemplateModeManger, Template
from ..android.capture import ScreenCapturer
from ..android.operators.base import Operator
import yaml

class TemplateController:
    """
    Controller 同时支持多个group的模板
    """
    def __init__(self, ctrl_cfg_path, full_screen_capturer, template_monitor_manager=None,
                 show_detect=False, show_history=False, show_state=False):
        self.template_mode_manager: TemplateModeManger = \
            self._init_mode_manager(ctrl_cfg_path, full_screen_capturer, template_monitor_manager)
        self.show_detect = show_detect
        self.show_history = show_history
        self.show_state = show_state

        self.pause = False

    def _init_mode_manager(self, cfg_path, full_screen_capturer, template_monitor_manager):
        with open(cfg_path, "r", encoding="utf8") as f:
            cfg = yaml.safe_load(f)
        template_modes = cfg.get("modes")
        return TemplateModeManger(template_modes, full_screen_capturer, template_monitor_manager)

    def init_dataset(self):
        pass

    def start(self, operator, interval_seconds=0.5, loops=None):
        while not self.pause:
            self.template_mode_manager.match(show_detail=self.show_detect)
            if self.show_history:
                print(self.template_mode_manager.matched_template_recoder)
            self.template_mode_manager.execute(operator, interval_seconds)
            if self.show_state:
                print(self.template_mode_manager.state_pool)

