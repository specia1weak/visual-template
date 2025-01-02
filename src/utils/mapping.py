from src.utils.image import ImageExpander


class CoordinateMapping:
    def __init__(self, img_expander: ImageExpander):
        self.img_expander = img_expander
        cut_config = img_expander.get_cut_config()
        self.cx, self.cy = cut_config["x"], cut_config["y"]
        self.cw, self.ch = cut_config["w"], cut_config["h"] # 默认附加了margin可以放心使用
        self.original_width = img_expander.original_width
        self.original_height = img_expander.original_height

    def normalize_x(self, x):
        return x / self.original_width

    def normalize_y(self, y):
        return y / self.original_height

    def map_xn(self, xn):
        xn = (xn - 0.5) * 1.3 + 0.5
        mapped_xn = (xn * self.cw + self.cx) / self.original_width
        return mapped_xn

    def map_yn(self, yn):
        mapped_yn = (yn * self.ch + self.cy) / self.original_height
        return mapped_yn

    def map_xyn(self, xyn):
        xn, yn = xyn
        return self.map_xn(xn), self.map_yn(yn)

    def map_drop_displacement(self, orig_displacement):
        return orig_displacement * self.ch / self.original_height

    def map_drop_speed(self, orig_speed):
        return orig_speed * self.ch / self.original_height



if __name__ == "__main__":
    cm = CoordinateMapping(ImageExpander("../../config/960x600-shot.json"))
    mapped_xyn = cm.map_xyn((1.0, 1.0))
    print(mapped_xyn)