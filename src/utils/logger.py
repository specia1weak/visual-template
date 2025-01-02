import logging
import os
from enum import Enum
from typing import Tuple
import cv2
from .singleton import Singleton


class OperateType(Enum):
    DETECT = "检测"
    EXECUTE = "执行"

# 这是可以记录整个操作流程的全局logger，需要logger请调用它
@Singleton
class GlobalLogger:
    def __init__(self):
        self.operations_log_name = None
        self._frame_dir = None

        logging.basicConfig(level=logging.DEBUG)
        self._file_logger: logging.Logger = None
        self.loop_count = 0
        self.loop_count_need_refresh = True
        self.operates_filter = {
            "执行", "检测", "矫正", "识别ed"
        }

    def set_config(self, operations_log_name=None, frame_dir=None):
        if operations_log_name is not None:
            self.operations_log_name = operations_log_name
            self._get_file_logger()
        if frame_dir is not None:
            self._frame_dir = frame_dir

    def _get_file_logger(self):
        if self._file_logger is None:
            file_handler = logging.FileHandler(self.operations_log_name, mode="w", encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            self._file_logger = logging.getLogger("operator")
            self._file_logger.addHandler(file_handler)
        return self._file_logger

    def _refresh_loop(self):
        if self.loop_count_need_refresh:
            self._file_logger.info(f"{self.loop_count:=^16}")
            self.loop_count_need_refresh = False

    def record_operation(self, loop_step: str = None, operation: str = None, xyn: Tuple = None, fid: int = None):
        if loop_step not in self.operates_filter:
            return
        if self._file_logger is None:
            return
        self._refresh_loop()
        if xyn is not None:
            self._file_logger.info(f"{loop_step}: cls[{operation}], ({xyn[0]:.4f}, {xyn[1]:.4f})->{fid}")
        else:
            self._file_logger.info(f"{loop_step}: cls[{operation}], {fid}")

    def record_frame(self, img):
        cv2.imwrite(os.path.join(self._frame_dir, str(self.loop_count) + "png"), img)

    def record_time(self, time_type, t_ms):
        if self._file_logger is None:
            return
        self._refresh_loop()
        self._file_logger.info(f"{time_type}: 耗时{t_ms:.2f}ms")

    def record_displacement(self, dyn):
        if self._file_logger is None:
            return
        self._refresh_loop()
        self._file_logger.info(f"dy位移: {dyn:.3f}")

    def record_anything(self, s: str):
        if self._file_logger is None:
            return
        self._refresh_loop()
        self._file_logger.info(s)

    def update_loop(self):
        self.loop_count_need_refresh = True
        self.loop_count += 1
