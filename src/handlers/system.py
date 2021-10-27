from core.handler import handle
import psutil


@handle("system/ram")
def get_ram():
    return psutil.virtual_memory()


@handle("system/cpu/count")
def get_cpu_count():
    return psutil.cpu_count()


@handle("system/cpu/percentage")
def get_cpu_percentage():
    return psutil.cpu_percent(interval=1)


@handle("system/cpu/freq")
def get_cpu_freq():
    return psutil.cpu_freq()


@handle("system/disk")
def get_disk():
    return psutil.disk_usage("/")
