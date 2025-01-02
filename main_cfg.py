from src.android.windows.hwnd import search_mumu
from src.templates.generate import TemplateConfigGenerator
from src.templates.components.comptype import OperationType, DetectorType
import keyboard

def configurate():
    template_config_generator = TemplateConfigGenerator("Test", search_mumu("MuMu模拟器1"), mode="test1")
    def call_a_config():
        try:
            template_config_generator.shot_and_config(
                detector   = DetectorType.FIXED_REGION,
                operations = [OperationType.TAP]
            )
        except Exception:
            print("本次配置失败")

    print("ctrl+alt+1呼唤一次截图配置; ctrl+alt+2终止" )
    keyboard.add_hotkey("ctrl+alt+1", call_a_config)
    keyboard.wait("ctrl+alt+2")

if __name__ == "__main__":
    configurate()
