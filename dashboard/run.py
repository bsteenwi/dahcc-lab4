import dash
from dash.dependencies import Output, Input
from dash import dcc, html, dcc
from datetime import datetime
import json
import plotly.graph_objs as go
from collections import deque
from flask import Flask, request
import pandas as pd
import numpy as np

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

MAX_DATA_POINTS = 10000
UPDATE_FREQ_MS = 1000

time = deque(maxlen=MAX_DATA_POINTS)
accel_x = deque(maxlen=MAX_DATA_POINTS)
accel_y = deque(maxlen=MAX_DATA_POINTS)
accel_z = deque(maxlen=MAX_DATA_POINTS)
time2 = deque(maxlen=MAX_DATA_POINTS)
activity_index = deque(maxlen=MAX_DATA_POINTS)
global buffer
buffer = pd.DataFrame()

app.layout = html.Div(
    [
        dcc.Markdown(
            children="""
            # Live Sensor Readings
            """
        ),
        dcc.Graph(id="live_graph"),
        dcc.Interval(id="counter", interval=UPDATE_FREQ_MS),
        
        dcc.Graph(id="index_graph"),
        dcc.Interval(id="counter2", interval=UPDATE_FREQ_MS),
        
    ]
)


@app.callback(Output("live_graph", "figure"), Input("counter", "n_intervals"))
def update_graph(_counter):
    data = [
        go.Scatter(x=list(time), y=list(d), name=name)
        for d, name in zip([accel_x, accel_y, accel_z], ["X", "Y", "Z"])
    ]

    graph = {
        "data": data,
        "layout": go.Layout(
            {
                "xaxis": {"type": "date"},
                "yaxis": {"title": "Acceleration ms<sup>-2</sup>"},
            }
        ),
    }
    
    return graph


@app.callback(Output("index_graph", "figure"), Input("counter2", "n_intervals"))
def update_graph(_counter):
    
    data2 = [
        go.Scatter(x=list(time2), y=list(d), name=name)
        for d, name in zip([activity_index], ["Activity index"])
    ]
    graph = {
        "data": data2,
        "layout": go.Layout(
            {
                "xaxis": {"type": "date"},
                "yaxis": {"title": "Activity index"},
            }
        ),
    }
    if (len(time) > 0):  #  cannot adjust plot ranges until there is at least one data point
        graph["layout"]["xaxis"]["range"] = [min(time), max(time)]
        graph["layout"]["yaxis"]["range"] = [
            min(activity_index),
            max(activity_index)]
    
    return graph

def calc_activity_index(signal_df, channels=["x", "y", "z"]):
    """
    Compute activity index of sensor signals.
    :param signal_df: dataframe housing desired sensor signals
    :param channels: channels of signal to compute activity index
    :return: dataframe housing calculated activity index
    """
    return np.var(signal_df[channels], axis=0).mean() ** 0.5

#def define_buffer(x,y,z,time):
#    global buffer
#    buffer = pd.concat([buffer, pd.DataFrame([{'x':x, 'y':y, 'z':z}])])
#    if len(buffer)>=50:
#        activity_index.append(calc_activity_index(buffer))
#        print(activity_index)
#        time2.append(time)
#        buffer = pd.DataFrame()

@server.route("/data", methods=["POST"])
def data():  # listens to the data streamed from the sensor logger
    if str(request.method) == "POST":
        #print(f'received data: {request.data}')
        data = json.loads(request.data)
        for d in data['payload']:
            if (d.get("name", None) == "accelerometer"):  #  modify to access different sensors
                ts = datetime.fromtimestamp(d["time"] / 1000000000)
                if len(time) == 0 or ts > time[-1]:
                    time.append(ts)
                    # modify the following based on which sensor is accessed, log the raw json for guidance
                    accel_x.append(d["values"]["x"])
                    accel_y.append(d["values"]["y"])
                    accel_z.append(d["values"]["z"])
                    
                    #define_buffer(d["values"]["x"],d["values"]["y"],d["values"]["z"],ts)
                    
    return "success"


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")