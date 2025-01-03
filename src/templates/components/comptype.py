from enum import Enum

from . import operations
from . import detectors
from . import monitors


class OperationType(Enum):
    TAP = operations.TapOperation
    DRAG = operations.DragOperation
    ADB_EVENT = operations.ADBKeyEventOperation
    KEY_TEXT = operations.ADBTextOperation
    KEY_SCREEN = operations.ScreenShotOperation
    KEY_TAP = operations.BoxesDataKeyTapOperation
    SLEEP = operations.SleepOperation
    KEY_NUMBER = operations.RecognizeNumberOperation
    NAME_DRAG_TILL = operations.RepeatDragTillRegionExists


class DetectorType(Enum):
    FIXED_REGION = detectors.FixedRegionDetector
    FIXED_DIFFER = detectors.FixedRegionDifferDetector
    EXIST_REGION = detectors.RegionExistsDetector
    WITHOUT_IMG = detectors.WithoutImageDetector
    BINARY_EXIST_REGION = detectors.BinaryRegionExistsDetector
