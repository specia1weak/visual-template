"""
检测历史记录，适时插入状态的一些记录
"""
import time
from abc import ABC, abstractmethod
from typing import List

from src.templates.common import MatchedTemplateRecorder


class TemplateMonitor(ABC):
    @abstractmethod
    def monitor(self, state_recoder: MatchedTemplateRecorder, state_pool: set):
        pass


class TemplateMonitorManager:
    def __init__(self, monitor_instances: List[TemplateMonitor] = None):
        self.monitor_instances: List[TemplateMonitor] = []
        if monitor_instances is not None:
            self.monitor_instances.extend(monitor_instances)

    def attach(self, template_monitor: TemplateMonitor):
        self.monitor_instances.append(template_monitor)

    def detach(self):
        self.monitor_instances.pop()

    def monitor(self, state_recoder: MatchedTemplateRecorder, state_pool: set):
        for monitor_instance in self.monitor_instances:
            monitor_instance.monitor(state_recoder, state_pool)


class RepeatCountMonitor(TemplateMonitor):
    def __init__(self, added_state, repeat_template, upto_count):
        self.repeat_template = repeat_template
        self.upto_count = upto_count
        self.added_state = added_state

    def monitor(self, state_recoder: MatchedTemplateRecorder, state_pool: set):
        if state_recoder.check_count(self.repeat_template, self.upto_count):
            state_pool.add(self.added_state)


class TimeCountMonitor(TemplateMonitor):
    def __init__(self, added_state, wait_seconds):
        self.added_state = added_state
        self.wait_seconds = wait_seconds
        time.perf_counter()
        self.last_perf_count = None

    def monitor(self, state_recoder: MatchedTemplateRecorder, state_pool: set):
        if self.last_perf_count is None:
            self.last_perf_count = time.perf_counter()
        else:
            curr_perf_count = time.perf_counter()
            diff_seconds = curr_perf_count - self.last_perf_count
            if diff_seconds >= self.wait_seconds:
                self.last_perf_count = curr_perf_count
                state_pool.add(self.added_state)


## 你也可以用继承的方式自定义一个Monitor，就像这样
class TestMonitor(TemplateMonitor):
    def monitor(self, state_recoder: MatchedTemplateRecorder, state_pool: set):
        if state_recoder.check_count("test_template", 4):
            state_pool.add("test_state")
