from src.templates.compare import MatchMethod
from src.templates.gui.base import ConfigUI

## 通用的图像信息配置
class TemplateMatchConfigUI(ConfigUI):
    def __init__(self):
        super().__init__()

    def create_widgets(self):
        self.build_text_input("template_name", "模板名称:")
        self.build_text_input("threshold", "检测阈值[0-1]", 0.94, float)
        self.build_combobox("match_method", "检测方案",
                            MatchMethod.TM_SQDIFF_NORMED.name,
                            tuple(MatchMethod.__members__.keys()))


## 通用的判正逻辑配置
class CommonInfoConfigUI(ConfigUI):
    def __init__(self):
        super().__init__()

    def create_widgets(self):
        self.build_combobox("priority", "优先级[0-9]:", 5, [x for x in range(0, 10)])
        self.build_combobox("contrary", "反逻辑", "否", ["否", "是"])
        self.build_text_input("precondition", "前件[逗号分割]", "")
        self.build_text_input("outcome", "产生[逗号分割]", "")
        self.build_text_input("consume", "消耗[逗号分割]", "")
