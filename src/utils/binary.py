import numpy as np


def _compute_dist_of_colors(color1, color2):
    return np.mean(np.abs((1.0 * color1 - color2)), axis=-1)


def binary_bg_and_words_colors(img):
    pixels = img.reshape(-1, 3)
    unique_colors, colors_count = np.unique(pixels, axis=0, return_counts=True)
    # 计算每个元素与目标值的平均差值
    diff = _compute_dist_of_colors(unique_colors[:, np.newaxis], unique_colors)

    # 定义一个函数来计算不同区间的加权和
    def weighted_sum(diff, threshold, weight):
        masks = diff <= threshold
        ret = []
        for mask in masks:
            ret.append(np.sum(colors_count[mask]))
        return np.array(ret) * weight

    # 计算不同区间的加权和
    # weighted_counts = weighted_sum(diff, 0, 0.7) # 这个可以优化成下面的
    weighted_counts = colors_count * 0.7
    weighted_counts += weighted_sum(diff, 5, 0.5)
    weighted_counts += weighted_sum(diff, 10, 0.3)

    bg_color = unique_colors[np.argmax(weighted_counts)]
    bg_diff = _compute_dist_of_colors(unique_colors, bg_color)
    bg_diff_normed = bg_diff / np.max(bg_diff)
    dist_score = (bg_diff_normed ** 2) * weighted_counts
    words_color = unique_colors[np.argmax(dist_score)]

    # 返回结果，向上取整
    return weighted_counts, bg_color, words_color


def mean_binary_img(img, bg_color=None, words_color=None):
    if bg_color is None or words_color is None:
        weighted_counts, bg_color, words_color = binary_bg_and_words_colors(img)
    words_diff = _compute_dist_of_colors(img, words_color)
    binary_threshold = _compute_dist_of_colors(bg_color, words_color) / 2
    binary_img = np.where(words_diff < binary_threshold, 255, 0).astype(np.uint8)
    return binary_img
