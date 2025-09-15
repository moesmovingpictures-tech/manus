import psutil
import time
import asyncio

async def log_system_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage("/")

    metrics = {
        "timestamp": int(time.time()),
        "cpu_percent": cpu_percent,
        "memory_percent": memory_info.percent,
        "disk_percent": disk_usage.percent,
        "memory_used_gb": round(memory_info.used / (1024**3), 2),
        "disk_used_gb": round(disk_usage.used / (1024**3), 2),
    }
    # In a real scenario, this would log to a file or a database
    print(f"System Metrics: {metrics}")
    return metrics

async def start_monitoring(interval_seconds=60):
    while True:
        await log_system_metrics()
        await asyncio.sleep(interval_seconds)


