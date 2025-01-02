from src.android.windows.hwnd import search_mumu
from src.templates.generate import TemplateConfigGenerator
from src.templates.components.comptype import OperationType, DetectorType


def configurate():
    TemplateConfigGenerator("TapTap", search_mumu("MuMu模拟器1"), mode="search").shot_and_config(
        detector   = DetectorType.FIXED_REGION,
        operations = [OperationType.KEY_TEXT]
    )

if __name__ == "__main__":
    configurate()
