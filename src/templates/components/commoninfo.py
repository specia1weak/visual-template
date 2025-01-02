from src.templates.gui.applications import CommonInfoConfigUI
import re


def split_dot(s):
    split_words = re.split(", *", s)
    split_words = [word for word in split_words if word]
    return split_words


def replace_items(items_list, ori, rep):
    for i, item in enumerate(items_list):
        if item == ori:
            items_list[i] = rep
    return items_list


class TemplateCommonInfo:
    @classmethod
    def generate(cls):
        config_ui = CommonInfoConfigUI()
        common_info = config_ui.query_config()

        common_info["contrary"] = {"否": False, "是": True}[common_info.get("contrary")]
        common_info["precondition"] = split_dot(common_info["precondition"])
        common_info["outcome"] = split_dot(common_info["outcome"])
        common_info["consume"] = split_dot(common_info["consume"])
        common_info["priority"] = int(common_info["priority"])

        return common_info

    def __init__(self, **params):
        self.contrary = None
        self.precondition = None
        self.outcome = None
        self.consume = None
        for key, value in params.items():
            setattr(self, key, value)
