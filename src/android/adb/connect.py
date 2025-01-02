from typing import List

from . import config
import subprocess

DEFAULT_MUMU_DEVICE_ID = "127.0.0.1:16384"



def _adb_prefix(device_id):
    _ADB = config.ADB_EXECUTOR
    command = [_ADB]
    if device_id is not None:
        command.append("-s")
        command.append(device_id)
    return command

def adb_cmd(params: List[str], device_id=None):
    command = _adb_prefix(device_id)
    command.extend(params)
    res = subprocess.check_output(command)
    return res

def list_devices():
    devices = subprocess.getoutput("adb devices")
    return devices


def connect_device(device_id):
    command = ["adb", "connect", str(device_id)]
    subprocess.check_call(command)

def disconnect_device(device_id):
    command = ["adb", "disconnect", str(device_id)]
    subprocess.check_call(command)

def stop_adb():
    subprocess.check_call("adb kill-server")

def start_adb():
    subprocess.check_call("adb start-server")

def restart_adb():
    """ restart adb server """
    stop_adb()
    start_adb()


