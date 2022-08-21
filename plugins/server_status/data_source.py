from typing import Dict

import psutil


def cpu_status() -> float:
    return psutil.cpu_percent(interval=1)


def memory_status() -> float:
    return psutil.virtual_memory().percent


def disk_usage() -> Dict[str, psutil._common.sdiskusage]:
    disk_parts = psutil.disk_partitions()
    disk_usages = {
        d.mountpoint: psutil.disk_usage(d.mountpoint) for d in disk_parts
    }
    return disk_usages
