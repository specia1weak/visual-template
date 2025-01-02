import subprocess




from .connect import _adb_prefix
def adb_tap(xy, device_id=None):
    x, y = str(int(xy[0])), str(int(xy[1]))
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "tap", x, y])
    subprocess.check_call(command)

def adb_swipe(xy, device_id=None):
    x, y = str(int(xy[0])), str(int(xy[1]))
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "tap", x, y])
    subprocess.check_call(command)

def adb_down(xy, device_id=None):
    x, y = str(int(xy[0])), str(int(xy[1]))
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "motionevent", "DOWN", x, y])
    subprocess.check_call(command)

def adb_move(xy, device_id=None):
    """
    注意不同的move调用之间的他们的xy间隔要尽可能小
    """
    x, y = str(int(xy[0])), str(int(xy[1]))
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "motionevent", "MOVE", x, y])
    import time
    st = time.perf_counter()
    subprocess.check_call(command)
    print(time.perf_counter() - st)

def adb_up(xy, device_id=None):
    """
    注意不同的move调用之间的他们的xy间隔要尽可能小
    """
    x, y = str(int(xy[0])), str(int(xy[1]))
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "motionevent", "UP", x, y])
    subprocess.check_call(command)

if __name__ == "__main__":
    from src.android.adb import adb_cmd
    size_str = adb_cmd(['shell', 'wm', 'size'])
    size_str = size_str.decode('utf-8').strip().replace("x", " ")
    size_str.split(" ")[-2:]
    # start_p = (200, 200)
    # end_p = (400, 400)
    #
    # diff_x = end_p[0] - start_p[0]
    # diff_y = end_p[1] - start_p[1]
    # adb_down(start_p)
    # for i in range(200):
    #     dx = dy = i * 1
    #     inter_p = start_p[0] + dx, start_p[1] + dy
    #     adb_move(inter_p)