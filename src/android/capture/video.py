import cv2
from .base import Capturer
from src.utils.image import ImageExpander


class VideoCapturer(Capturer):
    def __init__(self, x1, y1, w, h, video_path, sample_fps=20, skip_frames=None, post_address=None):
        self.x1 = x1
        self.y1 = y1
        self.w = w
        self.h = h
        self.video_path = video_path
        self.sample_fps = sample_fps
        self.skip_frames = skip_frames
        self.post_address = post_address

        self.video_obj = None
        self.frame_index = None
        self.video_fps = None
        self.interval = None
        self.skip_num_frames = None
        self.read_over = None
        self.init_env()

    @classmethod
    def from_image_expander(cls, image_expander: ImageExpander, video_path, sample_fps=20, skip_frames=None):
        cut_config = image_expander.get_cut_config()
        x1 = cut_config["x"]
        y1 = cut_config["y"]
        w = cut_config["w"]
        h = cut_config["h"]

        def post_address(image):
            return image_expander.reshape(image)

        return cls(x1, y1, w, h, video_path, sample_fps, skip_frames, post_address)

    def init_env(self):
        self.video_obj = cv2.VideoCapture(self.video_path)
        if not self.video_obj.isOpened():
            raise FileNotFoundError
        if self.skip_frames is not None:
            for _ in range(self.skip_frames):
                self.video_obj.read()
        self.frame_index = 0
        self.video_fps = self.video_obj.get(cv2.CAP_PROP_FPS)
        self.interval = self.video_fps / self.sample_fps
        self.skip_num_frames = 0
        self.read_over = False

    def capture(self):
        if self.read_over:
            return None

        frame = None
        while self.skip_num_frames < self.interval:
            ret, frame = self.video_obj.read()
            self.frame_index += 1
            if not ret:
                self.read_over = True
                return None
            self.skip_num_frames += 1

        self.skip_num_frames -= self.interval
        cut_frame = frame[self.y1: self.y1 + self.h, self.x1: self.x1 + self.w, ...]
        if self.post_address is not None:
            cut_frame = self.post_address(cut_frame)
        print(self.frame_index)
        return cut_frame

    def clear(self):
        self.video_obj.release()

    def reset(self):
        self.clear()
        self.init_env()

    def __del__(self):
        self.clear()