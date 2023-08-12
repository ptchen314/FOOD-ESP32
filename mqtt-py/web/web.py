import json
from flask_cors import *
from flask import Flask,render_template,request,Response,redirect,url_for
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'broker.mqttgo.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0 
mqtt = Mqtt(app)
DHT=0
Temp=0

@mqtt.on_connect()
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("FOOD/temp1")

@mqtt.on_message()
def on_message(client, userdata, msg):
    global Temp #全域宣告
    global DHT
    data = msg.payload.decode('utf-8') # 用UTF-8 decode
    tempdata = json.loads(data) # 轉成json
    print(tempdata)
    t1=(float(tempdata["temp1"])+float(tempdata["temp2"])+float(tempdata["temp3"]))/3
    Temp=int(t1)
    DHT=tempdata["DHT22"]

@app.route("/")
def main():
    global Temp
    global DHT
    print(Temp)
    return render_template("gauge-temperature.html", Temperature = Temp, DHT=DHT)

app.run(host='0.0.0.0', port=80)

