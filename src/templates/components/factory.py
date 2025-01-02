from typing import Union

from src.templates.components.commoninfo import TemplateCommonInfo
from src.templates.gui.utils import ScreenShotCropper
from src.templates.components.detectors import TemplateDetector
from src.templates.components.operations import TemplateOperation
from src.templates.components.comptype import OperationType, DetectorType


class OperationFactory:
    @staticmethod
    def generate_operation(cropper_with_img: ScreenShotCropper,
                           operation_type: Union[OperationType, str]) -> (dict, TemplateOperation):
        if isinstance(operation_type, str):
            operation_type = OperationType[operation_type]
        operation_kwargs = operation_type.value.generate(cropper_with_img)
        if operation_kwargs is None:
            return None
        return {
            "type": operation_type.name,
            "kwargs": operation_kwargs
        }
    @staticmethod
    def parse_operation(operation_config: dict):
        operation_type = operation_config.get("type")
        operation_type = OperationType[operation_type]

        operation_kwargs = operation_config.get("kwargs")
        return operation_type.value(**operation_kwargs)


class DetectorFactory:
    @staticmethod
    def generate_detector(cropper_with_img: ScreenShotCropper,
                          detector_type: Union[DetectorType, str]) -> (dict, TemplateDetector):
        if isinstance(detector_type, str):
            detector_type = OperationType[detector_type]
        detector_kwargs = detector_type.value.generate(cropper_with_img)
        if detector_kwargs is None:
            return None
        return {
            "type": detector_type.name,
            "kwargs": detector_kwargs
        }

    @staticmethod
    def parse_detector(detector_config: dict):
        detector_type = detector_config.get("type")
        detector_type = DetectorType[detector_type]

        detector_kwargs = detector_config.get("kwargs")
        return detector_type.value(**detector_kwargs)


class CommonInfoFactory:
    @staticmethod
    def generate_common_info():
        common_info = TemplateCommonInfo.generate()
        return common_info

    @staticmethod
    def parse_common_info(common_info: dict):
        return TemplateCommonInfo(**common_info)