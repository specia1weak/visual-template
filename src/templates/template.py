import json
import time
from typing import List, Dict, Union, Set

from .common import MatchedTemplateRecorder
from .components.commoninfo import TemplateCommonInfo
from .components.detectors import TemplateDetector
from .components.factory import DetectorFactory, OperationFactory, CommonInfoFactory
from .components.monitors import TemplateMonitorManager
from .components.operations import TemplateOperation
from ..android.capture import ScreenCapturer
from ..android.operators.base import Operator


class Template:
    """
    包括detector和operations和各种信息，detector可以把是否匹配，以及匹配的数据传给Dataset(通过update)
    operation也可以从Dataset中获取数据进行操作，因此在声明Template的时候可以传一个Dataset，后续的更改会比较方便
    """

    def __init__(self, template_name, template_config):
        self.template_name = template_name
        common_info = template_config.get("common_info")
        detector_config = template_config.get("detector")
        operations_config = template_config.get("operations")

        self.common_info: TemplateCommonInfo = CommonInfoFactory.parse_common_info(common_info)
        self.detector: TemplateDetector = DetectorFactory.parse_detector(detector_config)
        self.operations: List[TemplateOperation] = []
        for operation_config in operations_config:
            operation = OperationFactory.parse_operation(operation_config)
            self.operations.append(operation)

    def check_valid(self, state_pool: set):
        return state_pool.issuperset(self.common_info.precondition)

    def detect(self, full_screen_shot, dataset, update_dataset=True, show_detail=False):
        # print(self.template_name,end=": ")
        detect_exist, detect_data_dict = self.detector.detect(full_screen_shot, show_detail)
        if update_dataset and detect_data_dict is not None:
            dataset.update(detect_data_dict)
        return detect_exist

    def operate(self, operator, capturer, dataset, interval_seconds):
        for operation in self.operations:
            operation.execute(operator, capturer, dataset)
            time.sleep(interval_seconds)

    def update_state_pool(self, state_pool):
        self.consume_state_pool(state_pool)
        self.push_state_pool(state_pool)

    def push_state_pool(self, state_pool):
        state_pool.update(self.common_info.outcome)

    def consume_state_pool(self, state_pool: set):
        state_pool.difference_update(self.common_info.consume)


class TemplateMode:
    def __init__(self, mode_config_file):
        with open(mode_config_file, "r", encoding="utf8") as f:
            mode_config = json.load(f)

        self.mode_name = mode_config.get("mode_name")
        self.activated = mode_config.get("init_activated")
        templates_config = mode_config.get("templates")
        self.templates = {}
        for template_name, template_config in templates_config.items():
            self.templates[template_name] = Template(template_name, template_config)

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def match(self, full_screen_shot, dataset, state_pool, show_detail=False) -> List[Template]:
        """
        匹配img, 满足state_set的当前状态才可以匹配，最后给回匹配成功的TemplateImage
        """
        if not self.activated:
            return []

        matched_templates = []
        for template_name, template in self.templates.items():
            if template.check_valid(state_pool) and template.detect(full_screen_shot, dataset,
                                                                    update_dataset=True, show_detail=show_detail):
                matched_templates.append(template)

        return matched_templates

class SwiftTemplateMode:
    def __init__(self, mode_config_file, hwnd):
        with open(mode_config_file, "r", encoding="utf8") as f:
            mode_config = json.load(f)

        self.mode_name = mode_config.get("mode_name")
        self.activated = mode_config.get("init_activated")
        templates_config = mode_config.get("templates")
        self.templates = {}
        self.screen_capturers = {}
        for template_name, template_config in templates_config.items():
            template = Template(template_name, template_config)
            x,y,w,h = template.detector.region
            small_screen_capturer = ScreenCapturer(x,y,w,h,hwnd)
            td = template.detector
            td.region = (0, 0, w, h)  # EXPLAIN: 这里改动了template的属性
            td.x1, td.y1, td.w, td.h = (0, 0, w, h)  # EXPLAIN: 这里改动了template的属性
            self.templates[template_name] = template
            self.screen_capturers[template_name] = small_screen_capturer

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def match(self, state_pool=None) -> List[Template]:
        """
        匹配img, 满足state_set的当前状态才可以匹配，最后给回匹配成功的TemplateImage
        """
        if not self.activated:
            return []

        matched_images = []
        for template_name, template in self.templates.items():
            region_screen_img = self.screen_capturers[template_name].capture()  # 由事先准备的cap自行截图
            is_matched = template.detect(region_screen_img, state_pool)
            if is_matched:
                matched_images.append(template)

        return matched_images


class TemplateModeManger:
    def __init__(self, mode_config_files: List[str],
                 full_screen_capturer: ScreenCapturer,
                 monitor_manager: TemplateMonitorManager = None):
        self.state_pool = set()  # 状态集合
        self.matched_template_recoder = MatchedTemplateRecorder()
        self.dataset = {}  # 存放可供取用的data集合
        self.template_modes: Dict[str, TemplateMode] = {}
        self.screen_capturer = full_screen_capturer

        self.matched_template: Union[Template, None] = None

        self.monitor_manager = monitor_manager
        for mode_config_file in mode_config_files:
            template_mode = TemplateMode(mode_config_file)
            self.template_modes[template_mode.mode_name] = template_mode
        self._initialize_dataset()

    def _initialize_dataset(self):
        pass

    def _prepare_dataset(self):
        full_screen_img = self.screen_capturer.capture()
        self.dataset["full_screen_shot"] = full_screen_img

    def update_dataset(self, data):
        self.dataset.update(data)

    def update_state_pool(self, state_set):
        self.state_pool.update(state_set)

    def no_detect(self):
        time.sleep(1.)

    def match(self, valid_template_modes: Union[Set, None] = None, show_detail=False):
        ## 数据准备
        self._prepare_dataset()
        ## 数据获取
        full_screen_shot = self.dataset["full_screen_shot"]
        ## 匹配模板
        matched_templates_all_modes = []
        for mode_name, template_mode in self.template_modes.items():
            if valid_template_modes is not None and template_mode.mode_name not in valid_template_modes:
                continue
            matched_templates_a_mode = template_mode.match(full_screen_shot, self.dataset, self.state_pool, show_detail=show_detail)
            matched_templates_all_modes.extend(matched_templates_a_mode)
        if len(matched_templates_all_modes) == 0:
            self.matched_template = None
        else:
            # 优先级校验
            matched_templates_all_modes.sort(key=lambda x: x.common_info.priority)
            if show_detail:
                print("优先级: ", end="")
                for matched_template in matched_templates_all_modes:
                    print(f"{matched_template.template_name}: {matched_template.common_info.priority}", end=",")
                print()
            self.matched_template = matched_templates_all_modes[0]
        return self.matched_template

    def execute(self, absolute_operator: Operator, interval_seconds=1.):
        if self.matched_template is None:
            self.no_detect()
        else:
            print("执行: ", self.matched_template.template_name)
            self.matched_template.operate(absolute_operator, self.screen_capturer, self.dataset, interval_seconds)
            self.matched_template.update_state_pool(self.state_pool)
            self.matched_template_recoder.update_record(self.matched_template.template_name)
        if self.monitor_manager is not None:
            self.monitor_manager.monitor(self.matched_template_recoder, self.state_pool)

    def activate_mode(self, mode_name):
        mode = self.template_modes.get(mode_name, None)
        if mode is None:
            return
        mode.activate()

    def deactivate_mode(self, mode_name):
        mode = self.template_modes.get(mode_name, None)
        if mode is None:
            return
        mode.deactivate()
