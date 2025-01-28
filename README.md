# BoAmps-Carbon

BoAmps-Carbon is a Python package that tracks emissions and system resource usage during machine learning model training or any computational workload. It uses the `CodeCarbon` library to monitor carbon emissions and system metrics. After tracking, a csv file compatible with the BoAmps project is returned.

## Features

- Start and stop an emissions tracker.
- Automatically save tracking data, including emissions, CPU and GPU energy consumption, and system information, to a CSV file.
- Fetch real-time location and hardware details.

## Installation

1. Clone the repository or download the source code.
2. Install the package using `pip`:
```bash
pip install .
```

## Usage

```
from BoAmps_Carbon.tracker import TrackerUtility

tracker = TrackerUtility(project_name="My Experiment")
tracker.start_cracker()

# Simulate workload
import time
time.sleep(10)

tracker.stop_tracker("tracking_info.csv")
```