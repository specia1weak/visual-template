import subprocess
from .connect import _adb_prefix

def adb_text_input(text, device_id=None):
    command = _adb_prefix(device_id)
    command.extend(["shell", "input", "text"])
    command.append(text)
    subprocess.check_call(command)