"""
input.py 主要是adb shell input 相关的操作
"""
import subprocess
from enum import Enum
from .connect import _adb_prefix


class KeyEvent(Enum):
    HOME             = 3    # HOME键
    BACK             = 4    # 返回键
    # CALL             = 5    # 打开拨号应用
    # END_CALL         = 6    # 挂断电话
    VOLUME_UP        = 24   # 增加音量
    VOLUME_DOWN      = 25   # 降低音量
    # POWER            = 26   # 电源键
    # SLEEP            = 223  # 睡眠
    # CAMERA           = 27   # 拍照（需要在相机应用里）
    # EXPLORER         = 64   # 打开浏览器
    # MENU             = 82   # 菜单键
    # MEDIA_PLAY_PAUSE = 85   # 播放 / 暂停
    # MEDIA_STOP       = 86   # 停止播放
    # MEDIA_NEXT       = 87   # 播放下一首
    # MEDIA_PREVIOUS   = 88   # 播放上一首
    MOVE_HOME        = 122  # 移动编辑光标到行首或列表顶部
    MOVE_END         = 123  # 移动编辑光标到行末或列表底部
    DPAD_UP          = 19   # 向上方向键
    DPAD_DOWN        = 20   # 向下方向键
    DPAD_LEFT        = 21   # 向左方向键
    DPAD_RIGHT       = 22   # 向右方向键
    DPAD_CENTER      = 23   # 中心键
    DPAD_DOWN_LEFT   = 269  # 向左下方向键
    DPAD_DOWN_RIGHT  = 271  # 向右下方向键
    DPAD_UP_LEFT     = 268  # 向左上方向键
    DPAD_UP_RIGHT    = 270  # 向右上方向键

    ENTER            = 66
    BACKSPACE        = 67
    DELETE           = 112
    CLEAR            = 28   # 清除键
    CUT              = 277  # 剪切键
    COPY             = 278  # 复制键
    PASTE            = 279  # 粘贴键
    PAGE_UP          = 92   # 向上翻页
    PAGE_DOWN        = 93   # 向下翻页

    # MEDIA_PLAY       = 126  # 恢复播放
    # MEDIA_PAUSE      = 127  # 暂停播放
    APP_SWITCH       = 187  # 切换应用


def adb_key_event(keycode: KeyEvent, device_id=None):
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "keyevent"])
    command.append(str(keycode.value))
    subprocess.check_call(command)