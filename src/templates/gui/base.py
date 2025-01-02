from abc import abstractmethod

"""
使用ScreenShot时，指定一个numpy的img，之后cut_box, select_tap_point 可以框+选点，saved_img和tap_p就是最后的结果
"""
"""
模板项目文件应该是:
templates_matching
|-960x600  # w h
|-600x960
  |game1
    |-configs
      |-group1.json
      |-group2.json
      |-exception.json  # 异常处理文件
    |-templates
      |-group1
        |-template1.jpg
        |-template2.jpg
      |-group2
      |-exception
  |game2
|-1280x800
"""

import tkinter as tk
from tkinter import ttk


class ConfigUI:
    def __init__(self):
        self._rebuilded = False
        self._reseted = False
        self.rebuild()

    def reset(self):
        if self._reseted:
            return
        self.info_valid = True
        self._interrupt = True
        self.string_vars = {}
        self.components = {}
        self.post_address = {}
        self.master = tk.Tk()
        self.master.title("配置信息收集")
        self._reseted = True

    def rebuild(self):
        if self._rebuilded:
            return
        self.reset()
        self.compose_ui()
        self._rebuilded = True

    def _register_component(self, key, component):
        self.components[key] = component

    def _register_post_address(self, key, post_address):
        self.post_address[key] = post_address

    def build_text_input(self, key, info, default=None, post_address=None):
        label = tk.Label(self.master, text=info)
        label.pack()
        entry = tk.Entry(self.master)
        if default is not None:
            entry.insert(0, default)
        entry.pack()
        self._register_component(key, entry)
        if post_address is not None:
            self._register_post_address(key, post_address)
        return entry

    def build_combobox(self, key, info, default, options, post_address=None):
        label = tk.Label(self.master, text=info)
        label.pack()
        self.string_vars[info] = tk.StringVar(self.master)
        self.string_vars[info].set(default)  # 默认选项
        combobox = ttk.Combobox(self.master, textvariable=self.string_vars[info], values=options)
        combobox.pack()
        self._register_component(key, combobox)
        if post_address is not None:
            self._register_component(key, post_address)
        return combobox

    @abstractmethod
    def create_widgets(self):
        pass

    def _submit_info(self):
        # 获取用户输入的信息
        # self.config = {
        #     'template_name': self.template_name.get(),
        #     'priority': self.priority.get(),
        #     'threshold': self.threshold.get(),
        #     'match_method': self.match_method.get(),
        #     'precondition': self.precondition.get().split(','),
        #     'outcome': self.outcome.get().split(',')
        # }
        self.config = {
            key: component.get() for key, component in self.components.items()
        }
        for key, post_address in self.post_address.items():
            if post_address is not None:
                self.config[key] = post_address(self.config[key])
        self.master.destroy()  # 关闭窗口
        self._rebuilded = False
        self._reseted = False
        self._interrupt = False

    def compose_ui(self):
        self.create_widgets()
        self.submit_button = tk.Button(self.master, text="提交", command=self._submit_info)
        self.submit_button.pack()

    def query_config(self, check_valid=None):
        if not self._rebuilded:
            self.rebuild()
        while True:
            print("请输入")
            self.master.mainloop()
            if self._interrupt or check_valid is None or check_valid(self.config):
                break
            self.rebuild()
        if not self._interrupt:
            return self.config




