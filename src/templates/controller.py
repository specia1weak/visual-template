import json
import time
from typing import List, Dict, Union, Set
import keyboard

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
        self.exit_work = False

    def _init_mode_manager(self, cfg_path, full_screen_capturer, template_monitor_manager):
        with open(cfg_path, "r", encoding="utf8") as f:
            cfg = yaml.safe_load(f)
        template_modes = cfg.get("modes")
        return TemplateModeManger(template_modes, full_screen_capturer, template_monitor_manager)

    def _switch_working(self):
        self.pause = not self.pause

    def _exit_working(self):
        self.exit_work = True

    def init_dataset(self, **kwargs):
        self.template_mode_manager.update_dataset(kwargs)

    def init_state_pool(self, *args):
        self.template_mode_manager.update_state_pool(args)

    def bind_hotkey_to_switch_working(self, hotkey):
        keyboard.add_hotkey(hotkey, self._switch_working)

    def bind_hotkey_to_exit_working(self, hotkey):
        keyboard.add_hotkey(hotkey, self._exit_working)

    def run_once(self, operator, interval_seconds=0.5):
        if not self.pause:
            self.template_mode_manager.match(show_detail=self.show_detect)
            if self.show_history:
                print("历史:", self.template_mode_manager.matched_template_recoder)
            self.template_mode_manager.execute(operator, interval_seconds)
            if self.show_state:
                print("状态池", self.template_mode_manager.state_pool)

        if self.pause:
            self.template_mode_manager.no_detect()

    def start(self, operator, interval_seconds=0.5):
        while not self.exit_work:
            self.run_once(operator, interval_seconds)
