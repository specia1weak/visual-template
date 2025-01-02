# 临时将adb的路径添加到环境变量的PATH中
import os
from .config import ADB_PATH


def init_adb_env():
    os.environ['PATH'] = ADB_PATH + os.pathsep + os.environ.get('PATH', '')