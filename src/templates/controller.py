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
                 show_detect: Union[bool, None] = None,
                 show_history: Union[bool, None] = None,
                 show_state: Union[bool, None] = None):
        with open(ctrl_cfg_path, "r", encoding="utf8") as f:
            self.cfg = yaml.safe_load(f)
        self.template_mode_manager = TemplateModeManger(self.cfg.get("modes"), full_screen_capturer, template_monitor_manager)

        # init_args > cfg_args
        self.show_detect = show_detect if show_detect is not None else self.cfg.get("show_detect", None)
        self.show_history = show_history if show_history is not None else self.cfg.get("show_history", None)
        self.show_state = show_state if show_state is not None else self.cfg.get("show_state", None)

        self.pause = False
        self.exit_work = False


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
