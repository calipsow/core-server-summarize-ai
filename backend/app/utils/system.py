import psutil
import os
import threading
import subprocess
import GPUtil
from datetime import datetime


def get_system_metrics():
    # CPU Auslastung (in Prozent)
    cpu_usage = psutil.cpu_percent(interval=1)

    # RAM Auslastung (in MB)
    memory = psutil.virtual_memory()
    total_memory = memory.total / (1024**2)
    used_memory = memory.used / (1024**2)
    memory_usage_percent = memory.percent

    # Anzahl der laufenden Threads
    thread_count = threading.active_count()

    # Maximale Anzahl von Threads (kann über /proc/sys/kernel/threads-max ermittelt werden)
    try:
        with open("/proc/sys/kernel/threads-max", "r") as f:
            max_threads = int(f.read().strip())
    except FileNotFoundError:
        max_threads = "Unavailable"

    # Systemtemperatur (nur auf Linux-Systemen verfügbar, benötigt lm-sensors)
    try:
        temp_output = subprocess.check_output(
            "sensors", shell=True, stderr=subprocess.STDOUT
        ).decode("utf-8")
        temperatures = []
        for line in temp_output.splitlines():
            if "Core" in line and "°C" in line:
                temperatures.append(line)
        temp_data = temperatures
    except Exception:
        temp_data = "Temperature sensors not available"

    # Festplattenauslastung
    disk_usage = psutil.disk_usage("/")
    total_disk = disk_usage.total / (1024**3)  # in GB
    used_disk = disk_usage.used / (1024**3)  # in GB
    disk_usage_percent = disk_usage.percent

    # Netzwerk Auslastung
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent / (1024**2)  # in MB
    bytes_received = net_io.bytes_recv / (1024**2)  # in MB

    # System Uptime
    uptime_seconds = psutil.boot_time()

    # GPU Informationen
    try:
        gpus = GPUtil.getGPUs()
        gpu_data = []
        for gpu in gpus:
            gpu_data.append(
                {
                    "name": gpu.name,
                    "load": gpu.load * 100,  # Auslastung in Prozent
                    "memory_used_mb": int(gpu.memoryUsed),
                    "memory_total_mb": int(gpu.memoryTotal),
                    "temperature": gpu.temperature,
                    "uuid": gpu.uuid,
                }
            )
    except Exception:
        gpu_data = "GPU information not available"

    metrics = {
        "cpu_usage_percent": cpu_usage,
        "total_memory_mb": int(total_memory),
        "used_memory_mb": int(used_memory),
        "memory_usage_percent": memory_usage_percent,
        "active_threads": thread_count,
        "max_threads": max_threads,
        "temperature_data": temp_data,
        "total_disk_gb": int(total_disk),
        "used_disk_gb": int(used_disk),
        "disk_usage_percent": disk_usage_percent,
        "bytes_sent_mb": int(bytes_sent),
        "bytes_received_mb": int(bytes_received),
        "system_uptime_seconds": int(uptime_seconds),
        "gpu_data": gpu_data,
        "timestamp": int(datetime.now().timestamp()),
        "timestamp_human": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return metrics
