import os
from typing import Union, Tuple
import cv2
import numpy as np

class ScreenShotCropper:
    BOX_IMG_WINDOW = 'box'
    TAP_IMG_WINDOW = 'tap'
    CUT_IMG_WINDOW = 'cut'

    def __init__(self, img=None):
        self.img = img
        self.p1 = None
        self.p2 = None
        self.tap_p = None
        self.crop_box_image = None
        self.save_dir = None
        self.interrupt = False

    def reset_img(self, img=None):
        self.img = img
        self.p1 = None
        self.p2 = None
        self.tap_p = None
        self.crop_box_image = None
        self.interrupt = False

    def valid_shot(self):
        return not self.interrupt

    def crop_box(self, img=None) -> Union[None, Tuple[Tuple[int, int, int, int], np.ndarray]]:
        if not self.valid_shot():
            return
        if img is not None:
            self.img = img
        cv2.namedWindow(self.BOX_IMG_WINDOW)
        cv2.setMouseCallback(self.BOX_IMG_WINDOW, self.on_mouse_cut_box, self)
        cv2.imshow(self.BOX_IMG_WINDOW, self.img)
        cv2.waitKey(0)
        try:
            cv2.destroyWindow(self.BOX_IMG_WINDOW)
        except cv2.error as e:
            print("窗口被提前关闭")
            self.interrupt = True
            return None
        return self.p1 + self.p2, self.crop_box_image

    def select_tap_point(self, img=None) -> Union[None, Tuple[int, int]]:
        if not self.valid_shot():
            return
        if img is not None:
            self.img = img
        cv2.namedWindow(self.TAP_IMG_WINDOW)
        cv2.setMouseCallback(self.TAP_IMG_WINDOW, self.on_mouse_select_point, self)
        cv2.imshow(self.TAP_IMG_WINDOW, self.img)
        cv2.waitKey(0)
        try:
            cv2.destroyWindow(self.TAP_IMG_WINDOW)
        except cv2.error as e:
            print("窗口被提前关闭")
            self.interrupt = True
        return self.tap_p

    def drag_arrow(self, img=None) -> Union[None, Tuple[Tuple[int, int], Tuple[int, int]]]:
        if not self.valid_shot():
            return
        if img is not None:
            self.img = img
        cv2.namedWindow(self.BOX_IMG_WINDOW)
        cv2.setMouseCallback(self.BOX_IMG_WINDOW, self.on_mouse_drag_line, self)
        cv2.imshow(self.BOX_IMG_WINDOW, self.img)
        cv2.waitKey(0)
        try:
            cv2.destroyWindow(self.BOX_IMG_WINDOW)
        except cv2.error as e:
            print("窗口被提前关闭")
            self.interrupt = True
            return None
        return self.p1, self.p2

    def show_crop_box(self):
        if self.crop_box_image is not None and len(self.crop_box_image) > 0:
            cv2.imshow(self.CUT_IMG_WINDOW, self.crop_box_image)
            cv2.waitKey(0)
            cv2.destroyWindow(self.CUT_IMG_WINDOW)

    def set_save_dir(self, save_dir):
        self.save_dir = save_dir

    def get_save_path(self, image_name):
        return os.path.join(self.save_dir, f"{image_name}.jpg")

    def save(self, image_name):
        assert self.save_dir is not None, "请在save前set一下save_dir"
        impath = self.get_save_path(image_name)
        cv2.imwrite(impath, self.crop_box_image)

    @staticmethod
    def on_mouse_cut_box(event, x, y, flags, shot_obj):
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONUP):
            img2 = shot_obj.img.copy()
            if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
                shot_obj.p1 = (x, y)
                cv2.circle(img2, shot_obj.p1, 5, (0, 255, 0), 5)
                cv2.imshow(shot_obj.BOX_IMG_WINDOW, img2)
            elif event == cv2.EVENT_MOUSEMOVE and flags:  # 按住左键拖曳
                cv2.rectangle(img2, shot_obj.p1, (x, y), (255, 0, 0), 1)
                cv2.imshow(shot_obj.BOX_IMG_WINDOW, img2)
            elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
                shot_obj.p2 = (x, y)
                cv2.rectangle(img2, shot_obj.p1, shot_obj.p2, (0, 0, 255), 1)
                cv2.imshow(shot_obj.BOX_IMG_WINDOW, img2)
                min_x = min(shot_obj.p1[0], shot_obj.p2[0])
                min_y = min(shot_obj.p1[1], shot_obj.p2[1])
                width = abs(shot_obj.p1[0] - shot_obj.p2[0])
                height = abs(shot_obj.p1[1] - shot_obj.p2[1])
                cut_img = shot_obj.img[min_y:min_y + height, min_x:min_x + width]
                shot_obj.crop_box_image = cut_img

    @staticmethod
    def on_mouse_select_point(event, x, y, flags, shot_obj):
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONUP):
            img2 = shot_obj.img.copy()
            if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
                shot_obj.tap_p = (x, y)
                cv2.circle(img2, shot_obj.tap_p, 5, (0, 255, 0), 5)
                cv2.imshow(shot_obj.TAP_IMG_WINDOW, img2)

    @staticmethod
    def on_mouse_drag_line(event, x, y, flags, shot_obj):
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONUP):
            img2 = shot_obj.img.copy()
            if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
                shot_obj.p1 = (x, y)
                cv2.circle(img2, shot_obj.p1, 5, (0, 255, 0), 3)
                cv2.imshow(shot_obj.BOX_IMG_WINDOW, img2)
            elif event == cv2.EVENT_MOUSEMOVE and flags:  # 按住左键拖曳
                cv2.circle(img2, shot_obj.p1, 5, (0, 255, 0), 3)
                cv2.arrowedLine(img2, shot_obj.p1, (x, y), (255, 0, 0), 2, tipLength=0.05)
                cv2.imshow(shot_obj.BOX_IMG_WINDOW, img2)
            elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
                shot_obj.p2 = (x, y)
                cv2.circle(img2, shot_obj.p1, 5, (0, 255, 0), 3)
                cv2.arrowedLine(img2, shot_obj.p1, shot_obj.p2, (0, 0, 255), 2, tipLength=0.05)
                cv2.circle(img2, shot_obj.p2, 5, (0, 0, 255), 3)
                cv2.imshow(shot_obj.BOX_IMG_WINDOW, img2)