from src.android.windows.hwnd import search_mumu
from src.templates.generate import TemplateConfigGenerator
from src.templates.components.comptype import OperationType, DetectorType


def configurate():
    TemplateConfigGenerator("Test", search_mumu("MuMu模拟器1"), mode="test1").shot_and_config(
        detector   = DetectorType.FIXED_REGION,
        operations = [OperationType.TAP]
    )

if __name__ == "__main__":
    configurate()
