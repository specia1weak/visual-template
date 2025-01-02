from src.android.capture import ScreenCapturer
from src.android.windows.hwnd import search_mumu
from src.templates.controller import TemplateController
from src.android.operators import AutoMumuOperator, SafeDecorator
from src.android.adb import DEFAULT_MUMU_DEVICE_ID, init_adb_env

def run(cfg_path):
    init_adb_env()
    hwnd = search_mumu(window_title="MuMu模拟器1")
    with SafeDecorator(AutoMumuOperator(DEFAULT_MUMU_DEVICE_ID, hwnd)) as operator:
        operator_info = operator.get_info()
        full_screen_capturer = ScreenCapturer(0, 0, operator_info["w"], operator_info["h"], hwnd)
        template_controller = TemplateController(cfg_path, full_screen_capturer)
        template_controller.init_dataset(search_content="原神")
        template_controller.start(operator, interval_seconds=0.5)


if __name__ == "__main__":
    run("./cfg.yaml")
