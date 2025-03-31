import json
import pandas as pd
import logging
from flask import Flask, request
from datetime import datetime
import os

# Fully disable Flask's default request logs
log = logging.getLogger('werkzeug')
log.handlers.clear()  # Remove existing handlers
log.propagate = False  # Prevent logs from bubbling up

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


server = Flask(__name__)

ACTIVITY_INDEX_TIME = 5
buffer_x, buffer_y, buffer_z = [], [], []
activity_index, time2, time = [], [], []
accel_x, accel_y, accel_z = [], [], []

LAST_CALC_TIME_FILE = "last_calc_time.txt"

def calc_activity_index(df):
    return df.std().mean()  # Example function

def read_last_calc_time():
    """Reads last_calc_time from a file."""
    if os.path.exists(LAST_CALC_TIME_FILE):
        with open(LAST_CALC_TIME_FILE, "r") as f:
            timestamp = f.read().strip()
            if timestamp:
                return datetime.fromisoformat(timestamp)
    return None

def write_last_calc_time(timestamp):
    """Writes last_calc_time to a file."""
    with open(LAST_CALC_TIME_FILE, "w") as f:
        f.write(timestamp.isoformat())

@server.route("/data", methods=["POST"])
def data():
    global buffer_x, buffer_y, buffer_z

    # Read last_calc_time from the file
    last_calc_time = read_last_calc_time()

    data = json.loads(request.data)
    for d in data.get("payload", []):
        if d.get("name") == "accelerometer":
            ts = datetime.fromtimestamp(d["time"] / 1e9)  # Convert nanoseconds to seconds

            if not time or ts > time[-1]:
                time.append(ts)
                accel_x.append(d["values"]["x"])
                accel_y.append(d["values"]["y"])
                accel_z.append(d["values"]["z"])

                buffer_x.append(d["values"]["x"])
                buffer_y.append(d["values"]["y"])
                buffer_z.append(d["values"]["z"])

                if last_calc_time is None:
                    last_calc_time = ts
                    write_last_calc_time(last_calc_time)  # Initialize first time

                if (ts - last_calc_time).total_seconds() >= ACTIVITY_INDEX_TIME:
                    df = pd.DataFrame({'x': buffer_x, 'y': buffer_y, 'z': buffer_z})

                    ### UNCOMMENT HERE!!
                    #act_idx = calc_activity_index(df)
                    #activity_index.append(act_idx)
                    #logging.info(f"Timestamp: {ts}, Last call: {last_calc_time}, Activity Index: {act_idx}")

                    # Reset buffer
                    buffer_x.clear()
                    buffer_y.clear()
                    buffer_z.clear()

                    last_calc_time = ts  # Update timestamp
                    write_last_calc_time(last_calc_time)  # Save to file

    return "success"


# Run the app
if __name__ == "__main__":
    server.run(port=8000, host="0.0.0.0")
