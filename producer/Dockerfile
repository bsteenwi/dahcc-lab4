FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY run.py run.py
COPY accelerometer.json accelerometer.json 

CMD [ "python3", "run.py"]