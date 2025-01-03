from abc import ABC, abstractmethod
import math
from typing import List, Tuple

import numpy as np

import cv2
import yaml


class ImageExpander:
    def __init__(self, config_path=None):
        self.l1y = None
        self.l2y = None
        self.l1x1 = None
        self.l1x2 = None
        self.l2x1 = None
        self.l2x2 = None
        self.original_height = 700
        self.original_width = 1600
        self.final_height = 800
        self.final_width = 800
        self.margin = 1.2
        self.h_multiple = 2.76
        if config_path is not None:
            self.load_config(config_path)

    def load_config(self, config_path):
        setting = yaml.safe_load(open(config_path, 'r', encoding='utf8'))
        for k, v in setting.items():
            setattr(self, k, v)

    def _correct_config(self):
        self.l1x1, self.l1x2 = min(self.l1x1, self.l1x2), max(self.l1x1, self.l1x2)
        self.l2x1, self.l2x2 = min(self.l2x1, self.l2x2), max(self.l2x1, self.l2x2)
        if self.l1y > self.l2y:
            self.l1y, self.l2y = self.l2y, self.l1y
            self.l1x1, self.l1x2, self.l2x1, self.l2x2 = self.l2x1, self.l2x2, self.l1x1, self.l1x2

    def save_config(self, config_path):
        self._correct_config()
        attrs = self.__dict__
        print(attrs)
        yaml.dump(attrs, open(config_path, "w", encoding="utf8"))

    @staticmethod
    def _myexpand(img, my1, my2, ml1, mr1, ml2, mr2, h_multiple, final_w):
        """
        :param my1, my2: margin后图片的上下
        :param ml1, mr1: margin后图片上部分的左右
        :param ml2, mr2: margin后图片下部分的左右
        :param h_multiple:
        :param final_w:
        :return:
        """
        stack = []
        inc_sum = 0
        for i in range(my1, my2 + 1):
            r = (i - my1 + 1) / (my2 - my1 + 1)  # 从0 到 1
            cur_multiple = 1 + r * (h_multiple - 1)
            increment = (cur_multiple - 1) / cur_multiple
            inc_sum += increment
            if inc_sum > 1:
                inc_sum -= 1
                continue
            dl, dr = ml2 - ml1, mr2 - mr1
            row = img[i, ml1 + math.ceil(dl * r): mr1 + math.ceil(dr * r), :]  # w 可能需要截取不同的
            row = row[None, ...]
            new_row = cv2.resize(row, (final_w, 1))  # resize的w要相同
            stack.append(new_row)
        new_img = np.concatenate(stack, axis=0)
        return new_img

    def _apply_margin(self, l1, r1, l2, r2):
        ml1 = round((r1 + l1) // 2 - ((r1 - l1) // 2 * self.margin))
        mr1 = round((r1 + l1) // 2 + ((r1 - l1) // 2 * self.margin))
        ml2 = round((r2 + l2) // 2 - ((r2 - l2) // 2 * self.margin))
        mr2 = round((r2 + l2) // 2 + ((r2 - l2) // 2 * self.margin))
        return ml1, mr1, ml2, mr2

    def cut_and_reshape(self, img):
        self._correct_config()
        y1, y2 = self.l1y, self.l2y
        l1, r1 = self.l1x1, self.l1x2
        l2, r2 = self.l2x1, self.l2x2
        # 使用margin留白
        ml1, mr1, ml2, mr2 = self._apply_margin(l1, r1, l2, r2)

        return cv2.resize(
            self._myexpand(img, y1, y2, ml1, mr1, ml2, mr2, h_multiple=self.h_multiple, final_w=self.final_width),
            (self.final_width, self.final_height)
        )

    def get_cut_config(self):
        self._correct_config()
        y1, y2 = self.l1y, self.l2y
        l1, r1 = min(self.l1x1, self.l1x2), max(self.l1x1, self.l1x2)
        l2, r2 = min(self.l2x1, self.l2x2), max(self.l2x1, self.l2x2)
        ml1, mr1, ml2, mr2 = self._apply_margin(l1, r1, l2, r2)

        return {
            "x": ml2,
            "y": y1,
            "w": mr2 - ml2,
            "h": y2 - y1
        }

    def reshape(self, cut_img):
        h, w, c = cut_img.shape
        y1, y2 = 0, h - 1
        l1, r1 = min(self.l1x1, self.l1x2), max(self.l1x1, self.l1x2)
        l2, r2 = min(self.l2x1, self.l2x2), max(self.l2x1, self.l2x2)
        ml1, mr1, ml2, mr2 = self._apply_margin(l1, r1, l2, r2)
        l1 = ml1 - ml2
        r1 = mr1 - ml2
        l2 = 0
        r2 = w - 1
        return cv2.resize(
            self._myexpand(cut_img, y1, y2, l1, r1, l2, r2, h_multiple=self.h_multiple, final_w=self.final_width),
            (self.final_width, self.final_height)
        )


class ExpanderGenerator:
    RESHAPE_IMG_WINDOW = 'setting'
    LINE_IMG_WINDOW = 'line'
    POINT_IMG_WINDOW = 'point'
    DRAW_IMG_WINDOW = 'draw'

    def __init__(self, img):
        self.ori_img = img
        self.steps_img = [None for _ in range(6)]  # 线1， 线2， 4个点
        self.num_steps = -1

        self.saved_img = None  # 确认后的图像
        self.interrupt = False  # 可视化操作终止信号
        self.image_expander = ImageExpander()
        h, w, c = img.shape
        self.image_expander.original_height = h
        self.image_expander.original_width = w

    def reset_img(self, img=None):
        self.ori_img = img
        self.steps_img = [None for _ in range(6)]
        self.num_steps = -1
        self.saved_img = None  # 确认后的图像
        self.interrupt = False

    def read_setting(self, path):
        self.image_expander = ImageExpander(path)

    def valid_shot(self):
        return not self.interrupt

    def visualize_setting(self, img=None):
        if not self.valid_shot():
            return
        if img is not None:
            self.ori_img = img

        while self.num_steps < 5:
            window_name = self.RESHAPE_IMG_WINDOW
            # 提前配置好窗口
            cv2.namedWindow(window_name)
            cv2.setMouseCallback(window_name, self._on_mouse_update, self)
            # 获取上一步的图像
            cur_img = self.cur_step_img()
            if cur_img is None:
                print("操作错误, 返回上一步")
                self.last_step()
                cur_img = self.cur_step_img()
            cv2.imshow(window_name, cur_img)
            cv2.waitKey()
            self.next_step()
        try:
            cv2.destroyWindow(self.RESHAPE_IMG_WINDOW)
        except cv2.error as e:
            print("窗口被提前关闭")
            self.interrupt = True
        return self.image_expander

    def save_config(self, path):
        self.image_expander.save_config(path)
        return self.image_expander

    def get_config(self):
        return self.image_expander

    def cur_step_img(self):
        cur_img = self.ori_img if self.num_steps == -1 else self.steps_img[self.num_steps]
        return cur_img

    def update_step(self, x, y):
        img_temp = self.cur_step_img().copy()
        h, w, c = img_temp.shape
        if self.num_steps == -1:
            cv2.line(img_temp, (0, y), (w, y), (0, 0, 255), 1)
            self.image_expander.l1y = y
        if self.num_steps == 0:
            cv2.line(img_temp, (0, y), (w, y), (0, 255, 255), 1)
            self.image_expander.l2y = y
        if self.num_steps == 1:
            cv2.circle(img_temp, (x, self.image_expander.l1y), 2, (255, 255, 0), 2)
            self.image_expander.l1x1 = x
        if self.num_steps == 2:
            cv2.circle(img_temp, (x, self.image_expander.l1y), 2, (255, 255, 0), 2)
            self.image_expander.l1x2 = x
        if self.num_steps == 3:
            cv2.circle(img_temp, (x, self.image_expander.l2y), 2, (255, 0, 0), 2)
            self.image_expander.l2x1 = x
        if self.num_steps == 4:
            cv2.circle(img_temp, (x, self.image_expander.l2y), 2, (255, 0, 0), 2)
            self.image_expander.l2x2 = x

        self.steps_img[self.num_steps + 1] = img_temp
        return img_temp

    def next_step(self):
        self.num_steps += 1

    def last_step(self):
        self.num_steps -= 1

    @staticmethod
    def _on_mouse_update(event, x, y, flags, shot_obj):
        if event in (cv2.EVENT_LBUTTONDOWN,):
            ### 消费按键事件：点击 拖拽 松手 都指定他的y作为结果
            img_temp = shot_obj.update_step(x, y)
            cv2.imshow(shot_obj.RESHAPE_IMG_WINDOW, img_temp)

    @staticmethod
    def _on_mouse_set_point(event, x, y, flags, shot_obj):
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONUP):
            img2 = shot_obj.img.copy()
            if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
                shot_obj.tap_p = (x, y)
                cv2.circle(img2, shot_obj.tap_p, 5, (0, 255, 0), 5)
                cv2.imshow(shot_obj.TAP_IMG_WINDOW, img2)


class DrawItem(ABC):
    @abstractmethod
    def draw(self, img):
        pass


class DrawHorizonLine(DrawItem):
    def __init__(self, yn, strong=0.066, bgr_color: Tuple = (128, 128, 128)):
        self.yn = yn
        self.strong = strong
        self.bgr_color = bgr_color

    def draw(self, img):
        h, w, c = img.shape
        strong = round(h * self.strong) if self.strong < 1 else self.strong
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        color = self.bgr_color
        y = round(h * self.yn)
        cv2.line(overlay, (0, y), (w, y), color, strong)
        img = cv2.addWeighted(overlay, alpha=0.3, src2=img, beta=1, gamma=0)
        return img


class ImageDrawer:
    def __init__(self, *draw_items):
        if draw_items is not None:
            self.draw_items: List[DrawItem] = [*draw_items]
        else:
            self.draw_items: List[DrawItem] = []

    def add_item(self, item):
        self.draw_items.append(item)

    def pop_item(self):
        self.draw_items.pop()

    def draw(self, img):
        for draw_item in self.draw_items:
            img = draw_item.draw(img)
        return img


def simple_binarize_image(img, threshold=127):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary


if __name__ == "__main__":
    img = cv2.imread("img.png")
    eg = ExpanderGenerator(img)
    image_expander = eg.visualize_setting()
    new_img = image_expander.cut_and_reshape(img)
    cv2.imshow("1", new_img)
    cv2.waitKey()
    # image_expander.save_config("./abc.yaml")
