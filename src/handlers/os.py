from core.handler import handle
import os
from datetime import datetime
import psutil


@handle("os/name")
def get_name():
    return os.uname().nodename


@handle("os/kernel")
def get_kernel():
    return os.uname().release


@handle("os/user")
def get_user():
    return psutil.Process().username()


@handle("os/boottime")
def get_boottime():
    return datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")


@handle("os/processes")
def get_processes():
    return psutil.Process().as_dict()
