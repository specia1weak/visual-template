from typing import Union, Tuple, List, Any

import cv2
import numpy as np

from enum import Enum

from cv2 import UMat, Mat
from numpy import ndarray, dtype, integer, floating


class MatchMethod(Enum):
    TM_SQDIFF_NORMED: int = cv2.TM_SQDIFF_NORMED  # 敏感亮度
    TM_CCOEFF_NORMED: int = cv2.TM_CCOEFF_NORMED  # 敏感轮廓
    MASK_CMP = "mask_cmp"


"""One of [TM_SQDIFF, TM_SQDIFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_CCOEFF, TM_CCOEFF_NORMED]"""


def search_template(template, background, method: Union[str, MatchMethod], theta=0.9) -> Tuple[
    List[Tuple[Any, Any, Any, Any]], Union[UMat, Mat, ndarray]]:
    if isinstance(method, str):
        method = MatchMethod[method]
    h, w = template.shape[:2]
    res = cv2.matchTemplate(background, template, method.value)
    if method == MatchMethod.TM_SQDIFF_NORMED:
        candidates = np.where(res < (1 - theta))
    elif method == MatchMethod.TM_CCOEFF_NORMED:
        candidates = np.where(res >= theta)
    final_xy_points = []
    # print(np.max(res))

    INF_DIST = 9999
    for x1, y1 in zip(candidates[1], candidates[0]):
        min_dist = INF_DIST
        for x2, y2 in final_xy_points:
            dist = abs(x1 - x2) + abs(y1 - y2)
            min_dist = min(min_dist, dist)
        if min_dist >= 10:
            final_xy_points.append((x1, y1))
    final_xyxy_boxes = [(x, y, x + w, y + h) for x, y in final_xy_points]
    return final_xyxy_boxes, res


def compare_similarity_with_template(target, template, method: Union[str, MatchMethod]):
    if isinstance(method, str):
        method = MatchMethod[method]

    similarity_result = 0.
    if method == MatchMethod.TM_CCOEFF_NORMED:
        similarity_result = cv2.matchTemplate(target, template, method=method.value)
        similarity_result = similarity_result.item()
    elif method == MatchMethod.TM_SQDIFF_NORMED:
        similarity_result = 1 - cv2.matchTemplate(target, template, method=method.value)
        similarity_result = similarity_result.item()
    elif method == MatchMethod.MASK_CMP:
        saved_img = StoredImage(template)
        similarity_result = saved_img.soft_imcmp(target)
    # print(similarity_result)
    return similarity_result


class StoredImage:
    def __init__(self, img, r=1):
        if isinstance(img, str):
            self.img = cv2.imread(img) * 1.0
        else:
            self.img = img * 1.0
        self.h, self.w = self.img.shape[:2]
        self.stack_region = r

        self.slice = self.init_shift_stack()
        self.mask = self.filter_no_use_pixel(self.slice)

        self.contour = self.init_contour()
        self.contour_mask = np.where(self.contour > 0, 1., 0.)

        print("有效像素点：", np.sum(self.mask), "/", self.h * self.w)
        self.num_valid_pixels = np.sum(self.mask)

    def init_shift_stack(self):
        img, r = self.img, self.stack_region
        imgs = []
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                # 向右偏移i次，向下偏移i次
                shifted_img = np.roll(np.roll(img, i, axis=1), j, axis=0)
                if i > 0:
                    shifted_img[:i, :] = shifted_img[i:i + 1, :]
                if j > 0:
                    shifted_img[:, :j] = shifted_img[:, j:j + 1]
                if i < 0:
                    shifted_img[i:, :] = shifted_img[i - 1:i, :]
                if j < 0:
                    shifted_img[:, j:] = shifted_img[:, j - 1:j]
                imgs.append(shifted_img)
        imgs = np.stack(imgs, axis=0)
        return imgs * 1.0

    def filter_no_use_pixel(self, region_slide):
        mask = np.sum(
            np.sqrt(np.var(region_slide, axis=0)),
            axis=-1
        )
        threshold = np.mean(mask) / 4
        mask = np.where(mask >= threshold, 1., 0.)
        return mask

    def same_shape(self, img2):
        img2 = cv2.resize(img2, dsize=(self.w, self.h))
        return img2

    # def _calc_distance_var(self, pixel_diff):
    #     # 判断位移是否集中
    #     min_index = np.argmin(pixel_diff, axis=0)
    #     min_list = []
    #     for i in range(9):
    #         min_list.append(np.sum((np.where(min_index == i, 1., 0.)) * self.mask))
    #     distribute = np.array(min_list)
    #     distribute = distribute / np.sum(distribute)
    #     print(distribute)
    #     print(np.var(distribute))

    def init_contour(self):
        image = np.array(self.img, dtype="uint8")
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, 50, 100)
        return edges

    def soft_imcmp(self, img2):
        # 这是一个允许微小位移的图片mse方法
        img2 = self.same_shape(img2) * 1.0
        rgb_diff = np.abs((self.slice - img2) / 255.)  # 由于self img已经是小数了
        rgb_diff = np.min(rgb_diff, axis=0)
        pixel_diff = np.mean(rgb_diff, axis=-1)
        pixel_diff *= self.mask
        image_diff = np.sum(pixel_diff) / self.num_valid_pixels
        similarity = 1 - 2 * image_diff  # -1, 1
        return similarity
