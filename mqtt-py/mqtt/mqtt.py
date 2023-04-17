from discordwebhook import Discord
from discordwebhook import Discord2 #DCwebhoooooooook
from dotenv import load_dotenv #dotenv
import os
import paho.mqtt.client as mqtt
import json
import requests
import logging


load_dotenv() #read ooooof
#Log
logging.basicConfig(filename='log/mqtt.log', encoding='utf-8', level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S')
#DC webhook
discord = Discord(url=os.getenv("DCWebhook"))
discord2 = Discord2(url=os.getenv("DCWebhook2"))

#Line notify登入
def lineNotifyMessage(msg):
    token = os.getenv("LINE_API_KEY")
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code


# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("FOOD/temp1")

def on_message(client, userdata, msg):
    # 轉換編碼utf-8才看得懂中文
    data = msg.payload.decode('utf-8');
    tempdata = json.loads(data)
    warn=tempdata["warn"]
    #1是開機，2是溫度異常，3是有人移動，4是正常，5是WiFi重連
    if  warn == "1":
        lineNotifyMessage("\n連線成功，ESP32已經開機完成")
        dcwebhook("\n連線成功，ESP32已經開機完成")
        tgbot("\n連線成功，ESP32已經開機完成")
        client.publish("FOOD/temp", "五號開機完成")
        temp_send(tempdata["temp1"],tempdata["temp2"],tempdata["temp3"],tempdata["DHT22"])
        thingspeak(tempdata["temp1"],tempdata["temp2"],tempdata["temp3"],tempdata["DHT22"])
    elif warn == "2":
        lineNotifyMessage("\n魚塭溫度異常，請檢查魚塭狀態！")
        dcwebhook("\n魚塭溫度異常，請檢查魚塭狀態！")
        tgbot("\n魚塭溫度異常，請檢查魚塭狀態！")
        temp_send(tempdata["temp1"],tempdata["temp2"],tempdata["temp3"],tempdata["DHT22"])
    elif warn == "3":
        temp_send(tempdata["temp1"],tempdata["temp2"],tempdata["temp3"],tempdata["DHT22"])
        thingspeak(tempdata["temp1"],tempdata["temp2"],tempdata["temp3"],tempdata["DHT22"])
    elif warn == "4":
        lineNotifyMessage("\n魚塭附近有人移動！")
        dcwebhook("\n魚塭附近有人移動！")
        tgbot("\n魚塭附近有人移動！")
    elif warn == "5":
        lineNotifyMessage("\n連線成功，ESP32已經重新連線")
        dcwebhook("\n連線成功，ESP32已經重新連線")
        tgbot("\n連線成功，ESP32已經重新連線")

#line發資料
def temp_send(t1,t2,t3,dht1):
    data=("\n5號 \n溫度計1:",t1, "℃\n溫度計2:",t2,"℃\n溫度計3:",t3 ,"℃\n濕度計1:",dht1," RH%")
    data=list(data)
    lineNotifyMessage("".join('%s' %id for id in data))
    dcwebhook("".join('%s' %id for id in data))
    tgbot("".join('%s' %id for id in data))
    logging.info( '溫度一： %s  溫度二： %s  溫度三： %s 濕度一： %s' , t1  , t2 , t3 , dht1 )
    # 轉成gauge用
    te1=(float(t1)+float(t2)+float(t3))/3
    te1=int(te1)
    client.publish("FOOD/temp1/gaugetemp", te1)
    client.publish("FOOD/temp1/gaugedht", dht1)
    webt=("{\"type\":\"temp\",\"temp\":\"",te1,"\"}")
    webdht=("{\"type\":\"DHT\",\"dht\":\"",dht1,"\"}")
    webt=list(webt)
    webdht=list(webdht)
    client.publish("FOOD/temp1/gaugetempweb", "".join('%s' %id for id in webt))
    client.publish("FOOD/temp1/gaugedhtweb", "".join('%s' %id for id in webdht))
#dc 發資料
def dcwebhook(msg):
    discord.post(
        content=msg,
        username="PT-Notify"
    )
    discord2.post(
        content=msg,
        username="PT-Notify"
    )
#tg發資料
def tgbot(message):
    apiToken = os.getenv("TGBOT")
    chatID = '-1001949741732'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
    except Exception as e:
        print(e)

def thingspeak(t1,t2,t3,dht1):
    httpget = {'field1': t1, 'field2': t2, 'field3': t3,'field4': dht1}
    r = requests.get(os.getenv("THINGSPEAK"), params = httpget)

# 連線設定
# 初始化地端程式
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("","")
#keep-alive超過60會自爆，這個server就是遜啦
client.connect("broker.MQTTGO.io", 1883, 60)
client.loop_forever()