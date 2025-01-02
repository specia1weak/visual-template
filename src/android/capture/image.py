import os
import cv2
from .base import Capturer
from src.utils.image import ImageExpander


class ImageDirCapturer(Capturer):
    def __init__(self, image_dir, post_address=None):
        self.post_address = post_address

        self.image_dir = image_dir
        self.image_list = None
        self.image_idx = None
        self.init_env()

    @classmethod
    def from_image_expander(cls, image_expander: ImageExpander, image_dir):
        cut_config = image_expander.get_cut_config()
        x1 = cut_config["x"]
        y1 = cut_config["y"]
        w = cut_config["w"]
        h = cut_config["h"]

        def post_address(image):
            return image_expander.reshape(image)

        return cls(image_dir, post_address)

    def init_env(self):
        self.image_list = []
        self.image_idx = 0
        image_files = os.listdir(self.image_dir)
        image_files.sort(key=lambda file: int(file.split(".")[0]))
        for image in image_files:
            self.image_list.append(os.path.join(self.image_dir, image))

    def capture(self):
        if self.image_idx >= len(self.image_list):
            return None
        image_file = self.image_list[self.image_idx]
        self.image_idx += 1
        image = cv2.imread(image_file)
        if self.post_address:
            image = self.post_address(image)
        return image

    def clear(self):
        del self.image_list

    def reset(self):
        self.clear()
        self.init_env()

    def __del__(self):
        self.clear()
