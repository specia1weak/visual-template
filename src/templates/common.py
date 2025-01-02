# 统一管理state的存放于消费的类
from typing import Union


class StatePool:
    def __init__(self):
        self.state_pool = set()


class Dataset:
    pass


# 记录历史的

from collections import deque
class MatchedTemplateItem:
    def __init__(self, name, count=1):
        self.name = name
        self.count = count

    def __str__(self):
        return f"[{self.name}:{self.count}]"


class MatchedTemplateRecorder:
    def __init__(self, maxlen=20):
        self.template_queue = deque(maxlen=maxlen)
        self.latest_item: Union[None, MatchedTemplateItem] = None

    def update_record(self, template_name):
        if self.latest_item is None:
            self.latest_item = MatchedTemplateItem(template_name)
        elif self.latest_item.name == template_name:
            self.latest_item.count += 1
        else:
            self.template_queue.append(self.latest_item)
            self.latest_item = MatchedTemplateItem(template_name)

    def check_count(self, template_name, upto_count):
        if self.latest_item is not None:
            return self.latest_item.name == template_name and self.latest_item.count >= upto_count
        return False

    def __str__(self):
        items = []
        for item in self.template_queue:
            items.append(str(item))
        if self.latest_item is not None:
            items.append(str(self.latest_item))
        return ", ".join(items)


if __name__ == "__main__":
    strdr = MatchedTemplateRecorder()
    strdr.update_record("1g")
    for _ in range(20):
        strdr.update_record("2as")
        strdr.update_record("2ass")
    print(strdr)
