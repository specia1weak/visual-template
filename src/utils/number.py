import os
import time

import cv2
import numpy as np

from src.utils.binary import mean_binary_img
from src.utils.singleton import Singleton
from src.utils.time import timer


class NumberRecognizer:
    def __init__(self, numbers_dir):
        self.numbers_templates = [[] for _ in range(10)]
        for number in os.listdir(numbers_dir):
            number_templates_dir = os.path.join(numbers_dir, number)
            for img_name in os.listdir(number_templates_dir):
                img_path = os.path.join(number_templates_dir, img_name)
                number_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                self.numbers_templates[int(number)].append(number_img)

    def cmp(self, img1, img2):
        img2 = cv2.resize(img2, dsize=(img1.shape[1], img1.shape[0]))
        ret = cv2.matchTemplate(img2, img1, method=cv2.TM_CCOEFF_NORMED)  # img1是模板，这个img1 和 2 的顺序一定不能换
        return ret.item()

    def recognize(self, img, confidence=0.5):
        max_sims = [0 for _ in range(10)]
        for i, a_number_template_dir in enumerate(self.numbers_templates):
            for number_img in a_number_template_dir:
                sim = self.cmp(number_img, img)
                max_sims[i] = max(max_sims[i], sim)
        max_sim = max(max_sims)
        if max_sim >= confidence:
            return max_sims.index(max_sim), max_sim
        else:
            return None

@Singleton
class ImageNumberSplitter:
    def __init__(self, numbers_dir="numbers"):
        self.numbers_dir = numbers_dir
        self._number_recognizer = NumberRecognizer(numbers_dir)

    def split_numbers_boxes(self, img, show=False):
        if isinstance(img, str):
            img = cv2.imread(img)
        binary_img = mean_binary_img(img)
        # negative_img = np.array(255 - binary_img, dtype="uint8")
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8,
                                                                                ltype=cv2.CV_32S)

        first_column = stats[:, 0]
        sorted_indices = np.argsort(first_column)
        sorted_stats = stats[sorted_indices]

        if show:
            show_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
            cv2.waitKey(0)
            for i in range(1, num_labels):  # 0是背景
                area = sorted_stats[i, cv2.CC_STAT_AREA]  # 4
                x = sorted_stats[i, cv2.CC_STAT_LEFT]  # 0
                y = sorted_stats[i, cv2.CC_STAT_TOP]  # 1
                width = sorted_stats[i, cv2.CC_STAT_WIDTH]  # 2
                height = sorted_stats[i, cv2.CC_STAT_HEIGHT]  # 3
                box_area = width * height
                # 打印连通区域的属性
                print(f"Component {i}: Area = {area}, "
                      f"Bounding box = ({x}, {y}, {width}, {height}),"
                      f" box_area: {box_area}, rate:{area / box_area: .4f}, wh_rate: {width / height: .4f}")
                cv2.rectangle(show_img, (x, y), (x + width, y + height), (0, 255, 0), 2)
                box = binary_img[y: y + height, x:x + width, ...]
                box = cv2.resize(box, (box.shape[1] * 5, box.shape[0] * 5))
                cv2.imshow("cut", box)
                cv2.imshow("img", show_img)
                cv2.waitKey()

        areas, xywhs = sorted_stats[1:, -1].tolist(), sorted_stats[1:, :-1].tolist()
        max_area = max(areas)
        numbers = []
        ret_areas = []
        ret_xywhs = []
        ret_sims = []
        box_imgs = [binary_img[y:y + h, x:x + w] for x, y, w, h in xywhs]
        for i, bimg in enumerate(box_imgs):
            if areas[i] < max_area / 5:
                continue
            ret = self._number_recognizer.recognize(bimg, 0.5)
            if ret is not None:
                num, similarity = ret
                numbers.append(num)
                ret_areas.append(areas[i])
                ret_xywhs.append(xywhs[i])
                ret_sims.append(similarity)

        return {
            "numbers": numbers,
            "areas": ret_areas,
            "xywhs": ret_xywhs,
            "similarity": ret_sims
        }


    def save_number_templates(self, img, show=False):
        binary_img = self._mean_binary_img(img)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8,
                                                                                ltype=cv2.CV_32S)
        first_column = stats[:, 0]
        sorted_indices = np.argsort(first_column)
        sorted_stats = stats[sorted_indices]


        for i in range(1, num_labels):  # 0是背景
            x = sorted_stats[i, cv2.CC_STAT_LEFT]  # 0
            y = sorted_stats[i, cv2.CC_STAT_TOP]  # 1
            width = sorted_stats[i, cv2.CC_STAT_WIDTH]  # 2
            height = sorted_stats[i, cv2.CC_STAT_HEIGHT]  # 3
            # 打印连通区域的属性
            cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 2)
            box = binary_img[y: y + height, x:x + width, ...]
            box = cv2.resize(box, (box.shape[1] * 5, box.shape[0] * 5))
            if show:
                cv2.imshow("cut", box)
                cv2.imshow("img", img)
                cv2.waitKey()
            cv2.imwrite(f"{self.numbers_dir}/{i}.png", box)
