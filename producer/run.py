import pandas as pd
import requests
import time

total_f=pd.read_json('accelerometer.json')

time.sleep(5)
while True:
    for i, row in total_f.iterrows():
        payload = {}
        payload['name']='accelerometer'
        payload['values'] = {}
        payload['values']['x'] = row.x
        payload['values']['y'] = row.y
        payload['values']['z'] = row.z
        payload['time'] = time.time_ns()
        data = {}
        data['payload'] = [payload]
        r = requests.post('http://consumer:8000/data', json=data)
        time.sleep(0.03125)