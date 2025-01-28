import time
from codecarbon import EmissionsTracker
import csv
from datetime import datetime
import platform
import os
import psutil
import requests
import pkg_resources


def get_cpu_model():
    system = platform.system()
    try:
        if system == "Linux":
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
        elif system == "Windows":
            import wmi
            c = wmi.WMI()
            for processor in c.Win32_Processor():
                return processor.Name
        elif system == "Darwin":
            import subprocess
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
    except Exception as e:
        print(f"Error fetching CPU model: {e}")
    return None


def extract_fields(tracker, emissions, duration):
    def get_field_or_none(obj, attr, default=None):
        return getattr(obj, attr, default)

    def get_location_info():
        try:
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                return {
                    "country_name": data.get("country"),
                    "country_iso_code": data.get("countryCode"),
                    "region": data.get("regionName"),
                    "longitude": data.get("lon"),
                    "latitude": data.get("lat"),
                }
        except Exception:
            pass
        return {"country_name": None, "country_iso_code": None, "region": None, "longitude": None, "latitude": None}

    try:
        codecarbon_version = pkg_resources.get_distribution("codecarbon").version
    except Exception:
        codecarbon_version = None

    location_info = get_location_info()
    cpu_power = get_field_or_none(tracker, "_cpu_power", 0)
    gpu_power = get_field_or_none(tracker, "_gpu_power", 0)
    ram_power = get_field_or_none(tracker, "_ram_power", 0)
    duration_hours = duration / 3600

    cpu_energy = cpu_power * duration_hours if cpu_power else None
    gpu_energy = gpu_power * duration_hours if gpu_power else None
    ram_energy = ram_power * duration_hours if ram_power else None

    ram_total_size = round(psutil.virtual_memory().total / (1024**3), 2)

    fields = {
        "run_id": get_field_or_none(tracker, "_experiment_id"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_name": tracker._project_name,
        "duration": duration,
        "emissions": emissions,
        "emissions_rate": emissions / duration if duration else None,
        "cpu_power": cpu_power,
        "gpu_power": gpu_power,
        "ram_power": ram_power,
        "cpu_energy": cpu_energy,
        "gpu_energy": gpu_energy,
        "ram_energy": ram_energy,
        "energy_consumed": float(get_field_or_none(tracker, "_total_energy", 0)),
        "country_name": location_info["country_name"],
        "country_iso_code": location_info["country_iso_code"],
        "region": location_info["region"],
        "cloud_provider": os.environ.get("CLOUD_PROVIDER", "None"),
        "cloud_region": os.environ.get("CLOUD_REGION", "None"),
        "os": platform.system(),
        "python_version": platform.python_version(),
        "codecarbon_version": codecarbon_version,
        "cpu_count": os.cpu_count(),
        "cpu_model": get_cpu_model(),
        "gpu_count": 0,
        "gpu_model": None,
        "longitude": location_info["longitude"],
        "latitude": location_info["latitude"],
        "ram_total_size": ram_total_size,
        "tracking_mode": get_field_or_none(tracker, "_tracking_mode"),
        "on_cloud": "Yes" if os.environ.get("CLOUD_PROVIDER") else "No",
        "pue": get_field_or_none(tracker, "_pue", 1.0),
        "extra": get_field_or_none(tracker, "_measure_power_method"),
        "kWh": "kWh",
    }
    return fields


class TrackerUtility:
    def __init__(self, project_name="BoAmps-Carbon Project"):
        self.tracker = EmissionsTracker(project_name=project_name)
        self.start_time = None

    def start_cracker(self):
        self.tracker.start()
        self.start_time = time.time()
        print("Tracker started.")

    def stop_tracker(self, output_csv="tracking_info.csv"):
        if self.start_time is None:
            raise ValueError("You must start the tracker before stopping it.")

        emissions = self.tracker.stop()
        duration = time.time() - self.start_time

        fields = extract_fields(self.tracker, emissions, duration)

        with open(output_csv, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields.keys())
            writer.writeheader()
            writer.writerow(fields)

        print(f"Tracking information saved to {output_csv}")
        return fields
