import math
import random
from collections.abc import Iterable
from typing import List, Tuple

from ..pyminitouch import BlitzDevice

from abc import ABC, abstractmethod, ABCMeta


class Operator(ABC):

    @abstractmethod
    def single(self, xys, fingers):
        pass

    @abstractmethod
    def down(self, xys, fingers):
        pass

    @abstractmethod
    def up(self, fingers):
        pass

    @abstractmethod
    def move(self, xys, fingers):
        pass

    @abstractmethod
    def tap(self, xy):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_info(self) -> dict:
        pass


class OperatorDecorator(Operator, ABC):

    @abstractmethod
    def single(self, xyns, fingers):
        pass

    @abstractmethod
    def down(self, xyns, fingers):
        pass

    @abstractmethod
    def up(self, fingers):
        pass

    @abstractmethod
    def move(self, xyns, fingers):
        pass

    @abstractmethod
    def tap(self, xy):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_info(self):
        pass


class OperatorDevice(Operator, ABC):

    @abstractmethod
    def single(self, xyns, fingers):
        pass

    @abstractmethod
    def down(self, xyns, fingers):
        pass

    @abstractmethod
    def up(self, fingers):
        pass

    @abstractmethod
    def move(self, xyns, fingers):
        pass

    @abstractmethod
    def tap(self, xy):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_info(self):
        pass


# class FakeOperator(Operator):
#     NUM_LANES = 7
#     MAX_FINGERS = 2
#
#     def __init__(self, device_id, xln, yln, log="logs/operate_logs/fake_log.txt"):
#         if device_id is None:
#             print("请注意MiniOperator获得了空id，不起作用")
#             self.width = 1280
#             self.height = 720
#         else:
#             self.width = 1280
#             self.height = 720
#
#         self.xln = xln
#         self.yln = yln
#         ## lanes
#         self.dx = None
#         self.lanes = None
#         self.init_lanes(self.width, self.height)
#         ## cd
#         self.fingers_cd = None
#         self.move_interval = None
#         self.cd_time = None
#         self.up_cd_time = None
#         self.lanes_cd = None
#         self.init_cd_time(cd_time=conf.CD_CYCLES)
#         ## log
#         self.loops = 0
#         self.last_loop = 0
#         self.log = log
#         self.clear_log()
#
#     def clear_log(self):
#         if self.log:
#             with open(self.log, "w", encoding="utf8") as f:
#                 pass
#
#     def init_lanes(self, width, height):
#         dx = (1 - 2 * self.xln) / self.NUM_LANES
#         self.dx = dx
#         self.lanes = [(
#             round((self.xln + dx / 2 + i * dx) * width),
#             round(self.yln * height)
#         ) for i in range(self.NUM_LANES)]
#         print(self.lanes)
#
#     def init_cd_time(self, cd_time=3, up_cd_time=1, mv_interval=1):
#         self.lanes_cd = [
#             0 for _ in range(self.NUM_LANES)
#         ]
#         self.cd_time = cd_time
#         self.move_interval = mv_interval
#         self.up_cd_time = up_cd_time
#         self.fingers_cd = [
#             0 for _ in range(self.MAX_FINGERS)
#         ]
#
#     def _transfer(self, xns, fingers):
#         if not isinstance(xns, Iterable):
#             xns = (xns,)
#         if not isinstance(fingers, Iterable):
#             fingers = (fingers,)
#         # 负责将xn 或 xns 转为 lane_id
#         transfered_xns = []
#         transfered_fingers = []
#         for xn, finger in zip(xns, fingers):
#             lane_id = self._calc_num_dx(xn)
#             if 0 <= lane_id <= 6 and self.lanes_cd[lane_id] == 0:
#                 transfered_xns.append(lane_id)
#                 transfered_fingers.append(finger)
#                 self.lanes_cd[lane_id] = self.cd_time
#
#         return transfered_xns, transfered_fingers
#
#     def _check_finger_cd(self, xns, fingers):
#         new_xns, new_fingers = [], []
#         for xn, finger in zip(xns, fingers):
#             if self.fingers_cd[finger] == 0:
#                 new_xns.append(xn)
#                 new_fingers.append(finger)
#                 self.fingers_cd[finger] = self.move_interval
#         return new_xns, new_fingers
#
#     def cool_down(self):
#         self.loops += 1
#         self.lanes_cd = [max(0, cd - 1) for cd in self.lanes_cd]
#         self.fingers_cd = [max(0, cd - 1) for cd in self.fingers_cd]
#         print(self.lanes_cd)
#
#     def filter_cd(self, xns):
#         "判断哪些xn才是cd好的"
#         if not isinstance(xns, Iterable):
#             xns = (xns,)
#         right_xns = []
#         for xn in xns:
#             lane_id = self._calc_num_dx(xn)
#             if 0 <= lane_id <= 6 and self.lanes_cd[lane_id] == 0:
#                 right_xns.append(True)
#             else:
#                 right_xns.append(False)
#         return right_xns
#
#     def _calc_num_dx(self, xn):
#         if isinstance(xn, tuple):
#             xn = xn[0]
#         if xn < 0.5:
#             num_dx = (xn - self.xln) / self.dx
#             return math.floor(num_dx)
#         else:
#             num_dx = ((1 - xn) - self.xln) / self.dx
#             return self.NUM_LANES - 1 - math.floor(num_dx)
#
#     def record_operate(self, operate, xn=None, finger=None):
#         if not conf.need_log:
#             return
#
#         title = None
#         if self.loops > self.last_loop:
#             self.last_loop = self.loops
#             title = "======={}========\n".format(self.loops)
#         if xn is None:
#             xn = "null"
#         else:
#             if not isinstance(xn, int):
#                 xn = self._calc_num_dx(xn)
#
#         if finger is None:
#             finger = "null"
#
#         if self.log is not None:
#             with open(self.log, "a", encoding="utf8") as f:
#                 if title:
#                     f.write(title)
#                 f.write("操作：{}, 轨道：{}, 手指：{}\n".format(operate, xn, finger))
#
#     def record_tasks(self, tasks: List[Task], prefix="识别"):
#         if not conf.need_log:
#             return
#
#         title = None
#         if self.loops > self.last_loop:
#             self.last_loop = self.loops
#             title = "======={}========\n".format(self.loops)
#
#         if self.log is not None:
#             with open(self.log, "a", encoding="utf8") as f:
#                 if title:
#                     f.write(title)
#                 for task in tasks:
#                     cls_name = task.get_type_name()
#                     lane_id = self._calc_num_dx(task.hit_xn)
#                     if task.finger_id is not None:
#                         f.write("{}：{}，轨道{}，手指匹配{}\n".format(prefix, cls_name, lane_id, task.finger_id))
#                     else:
#                         f.write("{}：{}，轨道{}\n".format(prefix, cls_name, lane_id))
#
#     def stop(self):
#         pass
#
#     def single(self, xns, fingers):
#         assert len(xns) <= self.MAX_FINGERS
#         lane_ids, fingers = self._transfer(xns, fingers)
#         for lid, fin in zip(lane_ids, fingers):
#             self.record_operate("single", xn=lid, finger=fin)
#         return fingers
#
#     def flick_down(self, xns, fingers):
#         """
#         输入flick检测xn值
#         等待适时机会，你可以调用flick_move 不同手指的移动目的地
#         一定要与flick_up flick_move配套使用，并且根据lane id 指定手指
#         """
#         lane_ids, fingers = self._transfer(xns, fingers)
#         for lid, fin in zip(lane_ids, fingers):
#             self.record_operate("down", xn=lid, finger=fin)
#         return fingers
#
#     def flick_move(self, xyns, fingers):
#         """
#        各个手指的滑动目的地，目的地仍然用xn，yn表示
#         """
#         for xyn, fin in zip(xyns, fingers):
#             self.record_operate("flick_mv", xn=xyn[0], finger=fin)
#
#     def slide_move(self, xns, fingers):
#         """
#         不考虑yn的移动
#         """
#         xns, fingers = self._check_finger_cd(xns, fingers)
#         for xn, fin in zip(xns, fingers):
#             self.record_operate("mv", xn=xn, finger=fin)
#
#     def flick_up(self, fingers, positions=None):
#         """
#         传入手指ids就行了, flick_up 后的一段时间不允许被按下
#         """
#         ban_lanes = []
#         if positions is not None:
#             for finger, position in zip(fingers, positions):
#                 lane_id = self._calc_num_dx(position)
#                 self.lanes_cd[lane_id] = self.up_cd_time  # EXPLAIN 我这里规定note end后面依旧有cd
#                 ban_lanes.append(lane_id)
#
#         if not isinstance(fingers, Iterable):
#             fingers = (fingers,)
#         for lan, fin in zip(ban_lanes, fingers):
#             self.record_operate("up", xn=lan, finger=fin)
#
#
# class NoxOperator(FakeOperator):
#     NUM_LANES = 7
#     MAX_FINGERS = 2
#
#     def __init__(self, device_id, xln, yln, cd_time=conf.CD_CYCLES, mv_interval=conf.MOVE_INTERVAL,
#                  log="logs/operate_logs/log.txt"):
#         super().__init__(device_id, xln, yln, log)
#         restart_adb(device_id)
#         self.device = BlitzDevice(device_id)
#         self.width = int(self.device.connection.max_x)
#         self.height = int(self.device.connection.max_y)
#
#         self.init_lanes(self.width, self.height)
#         self.init_cd_time(cd_time, mv_interval)
#
#     def single(self, xns, fingers):
#         assert len(xns) <= self.MAX_FINGERS
#         lane_ids, fingers = self._transfer(xns, fingers)
#         positions = [self.lanes[lane_id] for lane_id in lane_ids]
#         self.device.swift_tap(positions, fingers)
#         for lid, fin in zip(lane_ids, fingers):
#             self.record_operate("single", xn=lid, finger=fin)
#         return fingers
#
#     def flick_down(self, xns, fingers):
#         """
#         输入flick检测xn值
#         等待适时机会，你可以调用flick_move 不同手指的移动目的地
#         一定要与flick_up flick_move配套使用，并且根据lane id 指定手指
#         """
#         lane_ids, fingers = self._transfer(xns, fingers)
#         points = [(finger, *self.lanes[lane_id]) for lane_id, finger in zip(lane_ids, fingers)]
#         print("down", points)
#         self.device.swift_press(points)
#         for lid, fin in zip(lane_ids, fingers):
#             self.record_operate("down", xn=lid, finger=fin)
#         return fingers
#
#     def flick_move(self, xyns, fingers):
#         """
#        各个手指的滑动目的地，目的地仍然用xn，yn表示
#         """
#         points = [(finger, round(xyn[0] * self.width),
#                    round(xyn[1] * self.height)) for xyn, finger in zip(xyns, fingers)]
#         print("flick", points)
#         for xyn, fin in zip(xyns, fingers):
#             self.record_operate("flick_mv", xn=xyn[0], finger=fin)
#         self.device.swift_move(points)
#
#     def slide_move(self, xns, fingers):
#         """
#         不考虑yn的移动
#         """
#         xns, fingers = self._check_finger_cd(xns, fingers)
#         points = [(finger,
#                    round(xn * self.width),
#                    round(self.yln * self.height)) for xn, finger in zip(xns, fingers)]
#         for xn, fin in zip(xns, fingers):
#             self.record_operate("mv", xn=xn, finger=fin)
#         print("slide", points)
#         self.device.swift_move(points)
#
#     def flick_up(self, fingers, positions=None):
#         """
#         传入手指ids就行了, flick_up 后的一段时间不允许被按下
#         """
#         ban_lanes = []
#         if positions is not None:
#             for finger, position in zip(fingers, positions):
#                 lane_id = self._calc_num_dx(position)
#                 self.lanes_cd[lane_id] = self.up_cd_time
#                 ban_lanes.append(lane_id)
#
#         if not isinstance(fingers, Iterable):
#             fingers = (fingers,)
#         self.device.swift_release(fingers)
#         for lan, fin in zip(ban_lanes, fingers):
#             self.record_operate("up", xn=lan, finger=fin)
#         print("up", fingers)
#
#     def stop(self):
#         self.device.stop()
#
#
# class MumuOperator(FakeOperator):
#     NUM_LANES = 7
#     MAX_FINGERS = 10
#
#     def __init__(self, device_id, xln, yln,
#                  cd_time=conf.CD_CYCLES,
#                  mv_interval=conf.MOVE_INTERVAL, log="logs/operate_logs/log.txt"):
#         super().__init__(device_id, xln, yln, log)
#         restart_adb(device_id)
#         self.device = BlitzDevice(device_id)
#         self.width = int(self.device.connection.max_y)
#         self.height = int(self.device.connection.max_x)
#
#         self.init_lanes(self.width, self.height)
#         self.init_cd_time(cd_time, conf.CD_FLICK_UP, mv_interval)
#
#     def xy_reverse(self, positions, random_tap=False):
#         new_positions = []
#         for position in positions:
#             new_position = []
#             if len(position) == 3:
#                 new_position.append(position[0])
#             old_x, old_y = position[-2:]
#             new_x, new_y = self.height - old_y, old_x  # self.height是我们看上去的height  old_y 是我们看上去的y
#             if random_tap:
#                 random_dx = random.randint(-12, 12)
#                 random_dy = random.randint(-12, 12)
#                 new_x += random_dx
#                 new_y += random_dy
#             new_position.append(new_x)
#             new_position.append(new_y)
#             new_positions.append(new_position)
#         return new_positions
#
#     def xy_randn(self, positions, rx=False, ry=False):
#         new_positions = []
#         for position in positions:
#             new_position = []
#             if len(position) == 3:
#                 new_position.append(position[0])
#             old_x, old_y = position[-2:]
#             new_x = old_x + (random.randint(-5, 5) if rx else 0)
#             new_y = old_y + (random.randint(-5, 5) if ry else 0)
#             new_position.append(new_x)
#             new_position.append(new_y)
#             new_positions.append(new_position)
#         return new_positions
#
#     def single(self, xns, fingers):
#         assert len(xns) <= self.MAX_FINGERS
#         lane_ids, fingers = self._transfer(xns, fingers)
#         positions = [self.lanes[lane_id] for lane_id in lane_ids]
#         positions = self.xy_reverse(positions, random_tap=True)
#         self.device.swift_tap(positions, fingers, duration=0)
#         for lid, fin in zip(lane_ids, fingers):
#             self.record_operate("single", xn=lid, finger=fin)
#         return fingers
#
#     def flick_down(self, xns, fingers):
#         """
#         输入flick检测xn值
#         等待适时机会，你可以调用flick_move 不同手指的移动目的地
#         一定要与flick_up flick_move配套使用，并且根据lane id 指定手指
#         """
#         lane_ids, fingers = self._transfer(xns, fingers)
#         points = [(finger, *self.lanes[lane_id]) for lane_id, finger in zip(lane_ids, fingers)]
#         print("down", points)
#         points = self.xy_reverse(points)
#         self.device.swift_press(points)
#         for lid, fin in zip(lane_ids, fingers):
#             self.record_operate("down", xn=lid, finger=fin)
#         return fingers
#
#     def flick_move(self, xyns, fingers):
#         """
#        各个手指的滑动目的地，目的地仍然用xn，yn表示
#         """
#         points = [(finger, round(xyn[0] * self.width),
#                    round(xyn[1] * self.height)) for xyn, finger in zip(xyns, fingers)]
#         print("flick", points)
#         for xyn, fin in zip(xyns, fingers):
#             self.record_operate("flick_mv", xn=xyn[0], finger=fin)
#         points = self.xy_randn(points, rx=True, ry=False)
#         points = self.xy_reverse(points)
#         self.device.swift_move(points)
#
#     def slide_move(self, xns, fingers):
#         """
#         不考虑yn的移动
#         """
#         xns, fingers = self._check_finger_cd(xns, fingers)
#         points = [(finger,
#                    round(xn * self.width),
#                    round(self.yln * self.height)) for xn, finger in zip(xns, fingers)]
#         for xn, fin in zip(xns, fingers):
#             self.record_operate("mv", xn=xn, finger=fin)
#         print("slide", points)
#         points = self.xy_randn(points, ry=True)
#         points = self.xy_reverse(points)
#         self.device.swift_move(points)
#
#     def flick_up(self, fingers, positions=None):
#         """
#         传入手指ids就行了, flick_up 后的一段时间不允许被按下
#         """
#         ban_lanes = []
#         if positions is not None:
#             for finger, position in zip(fingers, positions):
#                 if isinstance(position, Iterable):
#                     position = position[0]
#                 lane_id = self._calc_num_dx(position)
#                 self.lanes_cd[lane_id] = self.up_cd_time
#                 ban_lanes.append(lane_id)
#
#         if not isinstance(fingers, Iterable):
#             fingers = (fingers,)
#         self.device.swift_release(fingers)
#         for lan, fin in zip(ban_lanes, fingers):
#             self.record_operate("up", xn=lan, finger=fin)
#         print("up", fingers)
#
#     def tap(self, point: Tuple[int, int]):
#         positions = [point]
#         positions = self.xy_reverse(positions, random_tap=True)
#         self.device.swift_tap(positions, [2], duration=100)
#
#     def stop(self):
#         self.device.stop()
#
#
# class FingerManager():
#     def __init__(self, max_fingers, operator: Operator):
#         self.fingers = None
#         self.max_fingers = max_fingers
#         self.fingers = [Finger(i) for i in range(self.max_fingers)]
#         self.operator = operator
#         self.FLICK_UP = conf.FLICK_UP
#         self.FLICK_LEFT = conf.FLICK_LEFT
#         self.FLICK_RIGHT = conf.FLICK_RIGHT
#
#     def request_free_finger(self, force=False):
#         free_finger = -1
#         for i, finger in enumerate(self.fingers):
#             if finger.state == Finger.STATE_FREE:
#                 free_finger = i
#                 break
#
#         if force:
#             dismiss_finger = self.fingers[0]
#             dismiss_finger.state = Finger.STATE_FREE
#             self.operator.flick_up([0], positions=[dismiss_finger.position])
#             free_finger = dismiss_finger
#         return free_finger
#
#     def reset_fingers(self):
#         self.fingers = [Finger(i) for i in range(self.max_fingers)]
#
#     def flick_move_up(self, finger_id):
#         finger = self.fingers[finger_id]
#         FLICK_UP = self.FLICK_UP
#         nxt_pos = (
#             finger.position[0] + FLICK_UP[0],
#             finger.position[1] + FLICK_UP[1]
#         )
#         finger.position = nxt_pos
#         self.operator.flick_move([nxt_pos], [finger_id])
#
#     def flick_move_left(self, finger_id):
#         finger = self.fingers[finger_id]
#         FLICK_UP = self.FLICK_LEFT
#         nxt_pos = (
#             finger.position[0] + FLICK_UP[0],
#             finger.position[1] + FLICK_UP[1]
#         )
#         finger.position = nxt_pos
#         self.operator.flick_move([nxt_pos], [finger_id])
#
#     def flick_move_right(self, finger_id):
#         finger = self.fingers[finger_id]
#         FLICK_RIGHT = self.FLICK_RIGHT
#         nxt_pos = (
#             finger.position[0] + FLICK_RIGHT[0],
#             finger.position[1] + FLICK_RIGHT[1]
#         )
#         finger.position = nxt_pos
#         self.operator.flick_move([nxt_pos], [finger_id])
#
#     def update_fingers(self):
#         # print("更新手指！！！")
#         # print(self.__str__())
#         release_fingers = []
#         move_up_fingers = []
#         move_left_fingers = []
#         move_right_fingers = []
#         # EXPLAIN：（1.0）判断hold和flick
#         for finger in self.fingers:
#             if finger.state in (Finger.STATE_HOLD, Finger.STATE_FLICK, Finger.STATE_LEFT, Finger.STATE_RIGHT):
#                 if finger.state_time > 1:
#                     if finger.state == Finger.STATE_FLICK:
#                         move_up_fingers.append(finger)
#                     elif finger.state == Finger.STATE_LEFT:
#                         move_left_fingers.append(finger)
#                     elif finger.state == Finger.STATE_RIGHT:
#                         move_right_fingers.append(finger)
#                 if finger.state_time == 1:
#                     release_fingers.append(finger)  # 说明需要松开这个手指
#                 finger.state_time -= 1
#         # print("释放",release_fingers)
#         # print("翻上",move_up_fingers)
#         # print("=============")
#         # EXPLAIN：（1.2）如有，则需要抬升Flick
#         if len(move_up_fingers) > 0:
#             move_up_positions = []
#             move_up_fingers_id = []
#             for finger in move_up_fingers:
#                 finger_id = finger.finger_id
#                 FLICK_UP = self.FLICK_UP
#                 nxt_pos = (
#                     finger.position[0] + FLICK_UP[0],
#                     finger.position[1] + FLICK_UP[1]
#                 )
#                 finger.position = nxt_pos
#                 # print(finger_id, "下一跳位置",nxt_pos)
#                 move_up_positions.append(nxt_pos)
#                 move_up_fingers_id.append(finger_id)
#             self.operator.flick_move(move_up_positions, move_up_fingers_id)
#         # EXPLAIN：（1.2）如有，则需要L-Flick
#         if len(move_left_fingers) > 0:
#             move_left_positions = []
#             move_left_fingers_id = []
#             for finger in move_left_fingers:
#                 finger_id = finger.finger_id
#                 FLICK_UP = self.FLICK_UP
#                 nxt_pos = (
#                     finger.position[0] + FLICK_UP[0],
#                     finger.position[1] + FLICK_UP[1]
#                 )
#                 finger.position = nxt_pos
#                 move_left_positions.append(nxt_pos)
#                 move_left_fingers_id.append(finger_id)
#             self.operator.flick_move(move_left_positions, move_left_fingers_id)
#         # EXPLAIN：（1.2）如有，则需要R-Flick
#         if len(move_right_fingers) > 0:
#             move_right_positions = []
#             move_right_fingers_id = []
#             for finger in move_right_fingers:
#                 finger_id = finger.finger_id
#                 FLICK_UP = self.FLICK_UP
#                 nxt_pos = (
#                     finger.position[0] + FLICK_UP[0],
#                     finger.position[1] + FLICK_UP[1]
#                 )
#                 finger.position = nxt_pos
#                 move_right_positions.append(nxt_pos)
#                 move_right_fingers_id.append(finger_id)
#             self.operator.flick_move(move_right_positions, move_right_fingers_id)
#         # EXPLAIN：（1.1）如有，则尽快松开Flick或者Hold
#         if len(release_fingers) > 0:
#             release_fingers_id = []
#             release_positions = []
#             for finger in release_fingers:
#                 finger_id = finger.finger_id
#                 finger.state = Finger.STATE_FREE
#                 release_fingers_id.append(finger_id)
#                 release_positions.append(finger.position)
#             self.operator.flick_up(release_fingers_id, positions=release_positions)
#
#     def match_finger(self, xns, max_cost=0.3):
#         """
#         :param xns: 被考虑的NOTE除了st ed 还有singe
#         :return:
#         """
#         INF_COST = 9999
#         # 需要重写！！
#         # 只有HOLD的手指可以参选
#         # 每个HOLD的手指通过匹配方案，要么HOLD手指没了，要么XNS没了
#
#         # EXPLAIN: HOLD手指
#         candidate_fingers = []
#         for finger in self.fingers:
#             if finger.state == Finger.STATE_HOLD:
#                 candidate_fingers.append(finger)
#
#         """
#         [
#         [0.1, 0.2] # 手指1
#         [0.9, 0.1] # 手指2
#         ]
#         """
#         res = [None for _ in self.fingers]
#         hold_fingers_num = len(candidate_fingers)
#         # print("当前hold手指数量", hold_fingers_num)
#         if hold_fingers_num == 0:
#             return res
#
#         costs = [[] for _ in range(hold_fingers_num)]
#
#         for i, finger in enumerate(candidate_fingers):
#             for xn in xns:
#                 current_cost = abs(finger.position - xn)
#                 costs[i].append(current_cost)
#
#         # 使用深搜
#         used = [False for _ in xns]
#         current_costs = []
#         current_match = []
#         # =======
#         min_cost = hold_fingers_num * INF_COST
#         best_costs = [INF_COST for _ in range(hold_fingers_num)]
#         best_match = [None for _ in range(hold_fingers_num)]
#
#         def dfs(fidx):
#             nonlocal min_cost, used, current_costs, current_match, best_match, best_costs
#             if fidx >= hold_fingers_num or len(current_match) >= len(xns):
#                 all_cost = sum(current_costs)
#                 if all_cost < min_cost:
#                     min_cost = all_cost
#                     best_costs = list(current_costs)
#                     best_match = list(current_match)
#                 return
#
#             for j, cost in enumerate(costs[fidx]):
#                 if used[j]:
#                     continue
#                 used[j] = True
#                 current_costs.append(cost)
#                 current_match.append(j)
#                 dfs(fidx + 1)
#                 current_match.pop(-1)
#                 current_costs.pop(-1)
#                 used[j] = False
#
#         dfs(0)
#
#         for finger, match, cost in zip(candidate_fingers, best_match, best_costs):
#             if cost <= max_cost:
#                 finger_id = finger.finger_id
#                 res[finger_id] = match
#
#         return res  # (手指1的匹配xn， 手指2的匹配xn)
#
#     def deep_copy(self):
#         new_finger_manager = FingerManager(self.max_fingers, self.operator)
#         new_finger_manager.fingers = [Finger(finger.state, finger.position, finger.state_time) for finger in
#                                       self.fingers]
#         return new_finger_manager
#
#     def __str__(self):
#         hline = "=========手指状态=========\n"
#         fingers_info = [f"手指-[{i}]@" + finger.__str__() for i, finger in enumerate(self.fingers)]
#         return hline + "\n".join(fingers_info)
