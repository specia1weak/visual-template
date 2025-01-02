### 点击随机化、坐标绝对包装、打日志
import numpy as np

from .base import OperatorDecorator, Operator
from src.utils.logger import GlobalLogger


class CoordinateNormalizeDecorator(OperatorDecorator):
    def __init__(self, operator: Operator):
        self.operator = operator
        device_info = self.get_info()
        self.original_width, self.original_height = device_info.get("w"), device_info.get("h")

    def _convert_norm2absolute(self, xyns):
        abs_xys = []
        for xn, yn in xyns:
            abs_x, abs_y = self.original_width * xn, self.original_height * yn
            abs_x, abs_y = round(abs_x), round(abs_y)
            abs_xys.append((abs_x, abs_y))
        return abs_xys

    def single(self, xyns, fingers):
        abs_xys = self._convert_norm2absolute(xyns)
        self.operator.single(abs_xys, fingers)

    def down(self, xyns, fingers):
        abs_xys = self._convert_norm2absolute(xyns)
        self.operator.down(abs_xys, fingers)

    def up(self, fingers):
        self.operator.up(fingers)

    def move(self, xyns, fingers):
        abs_xys = self._convert_norm2absolute(xyns)
        self.operator.move(abs_xys, fingers)

    def tap(self, xy):
        self.operator.tap(xy)

    def stop(self):
        self.operator.stop()

    def get_info(self):
        return self.operator.get_info()

class LogDecorator(OperatorDecorator):
    def __init__(self, operator: Operator, log_file):
        self.operator = operator
        self.log_file = log_file

        self.logger: GlobalLogger = GlobalLogger()
        self.logger.set_config(operations_log_name=self.log_file)

    def single(self, xyns, fingers):
        self.logger.record_operation(loop_step="执行", operation="single", xyn=xyns[0], fid=fingers[0])
        self.operator.single(xyns, fingers)

    def down(self, xyns, fingers):
        self.logger.record_operation(loop_step="执行", operation="down", xyn=xyns[0], fid=fingers[0])
        self.operator.down(xyns, fingers)

    def up(self, fingers):
        self.logger.record_operation(loop_step="执行", operation="up", xyn=None, fid=fingers[0])
        self.operator.up(fingers)

    def move(self, xyns, fingers):
        self.logger.record_operation(loop_step="执行", operation="move", xyn=xyns[0], fid=fingers[0])
        self.operator.move(xyns, fingers)

    def tap(self, xy):
        self.operator.tap(xy)

    def stop(self):
        self.operator.stop()

    def get_info(self):
        return self.operator.get_info()

class CoordinateRandomDecorator(OperatorDecorator):
    def __init__(self, operator: Operator, double_std_dev_pixel):
        self.operator = operator
        self.double_std_dev_pixel = double_std_dev_pixel
        device_info = self.operator.get_info()
        self.w, self.h = device_info.get("w"), device_info.get("h")
        self.double_std_dev_normed = self.double_std_dev_pixel * 2 / (self.w + self.h)

    @staticmethod
    def generate_gaussian(max_deviation, std_dev):
        # 生成一个高斯分布变量x
        x = np.random.normal(loc=0.0, scale=std_dev)
        # 限制x的值不超过最大偏差值
        x = max(-max_deviation, min(x, max_deviation))
        return x

    def _dxn_dyn_random(self):
        dxn = self.generate_gaussian(self.double_std_dev_normed, self.double_std_dev_normed / 2)
        dyn = self.generate_gaussian(self.double_std_dev_normed, self.double_std_dev_normed / 2)
        return dxn, dyn

    def _dy_dy_random(self):
        dx = self.generate_gaussian(self.double_std_dev_pixel, self.double_std_dev_pixel // 2)
        dy = self.generate_gaussian(self.double_std_dev_pixel, self.double_std_dev_pixel // 2)
        return dx, dy

    def _random_xyns(self, xyns):
        new_xyns = []
        for xn, yn in xyns:
            dxn, dyn = self._dxn_dyn_random()
            new_xyns.append((
                xn + dxn,
                yn + dyn
            ))
        return new_xyns

    def single(self, xyns, fingers):
        new_xyns = self._random_xyns(xyns)
        self.operator.single(new_xyns, fingers)

    def down(self, xyns, fingers):
        self.operator.down(xyns, fingers)

    def up(self, fingers):
        self.operator.up(fingers)

    def move(self, xyns, fingers):
        self.operator.move(xyns, fingers)

    def tap(self, xy):
        x, y = xy
        dx, dy = self._dy_dy_random()
        new_xy = x + dx, y + dy
        self.operator.tap(new_xy)

    def stop(self):
        self.operator.stop()

    def get_info(self):
        return self.operator.get_info()


class SafeDecorator(OperatorDecorator):
    def __init__(self, operator):
        self.operator = operator

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.up([fid for fid in range(10)])
        self.stop()

    def single(self, xyns, fingers):
        self.operator.single(xyns, fingers)

    def down(self, xyns, fingers):
        self.operator.down(xyns, fingers)

    def up(self, fingers):
        self.operator.up(fingers)

    def move(self, xyns, fingers):
        self.operator.move(xyns, fingers)

    def tap(self, xy):
        self.operator.tap(xy)

    def stop(self):
        self.operator.stop()

    def get_info(self):
        return self.operator.get_info()

