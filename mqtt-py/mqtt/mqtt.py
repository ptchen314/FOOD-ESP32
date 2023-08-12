from discordwebhook import Discord #DCwebhook
from dotenv import load_dotenv #dotenv
import os
import paho.mqtt.client as mqtt
import json
import requests
import logging


load_dotenv() #read .env file
#Log
logging.basicConfig(filename='log/mqtt.log', encoding='utf-8', level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S') #log file
#DC webhook login
discord = Discord(url=os.getenv("DCWebhook"))

#Line notify login
def lineNotifyMessage(msg):
    token = os.getenv("LINE_API_KEY") # set line notify token
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded" #set header
    }

    payload = {'message': msg } #set payload
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload) #post to line notify
    return r.status_code #return status code

#MQTT connect!
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("FOOD/temp1") #subscribe topic


#MQTT get message!
def on_message(client, userdata, msg):
    data = msg.payload.decode('utf-8') # 用UTF-8 decode
    tempdata = json.loads(data) # 轉成json
    warn=tempdata["warn"] # 警告編號
    # warn = "1" #start up
    # warn = "2" #temp abnormal
    # warn = "3" #humidity abnormal
    # warn = "4" #normal
    # warn = "5" #WiFi reconnect
    if  warn == "1":
        lineNotifyMessage("\n連線成功，ESP32已經開機完成") #line發資料
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


#discord send message
def dcwebhook(msg):
    discord.post(
        content=msg, # 訊息內容
        username="PT-Notify" # 修改Webhook名稱
    )

#telegram send message
def tgbot(message):
    apiToken = os.getenv("TGBOT") #bot token
    chatID = os.getenv("TGCHATID") #聊天室編號
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message}) #try to send message
    except Exception as e:
        print(e) #fuck up

def thingspeak(t1,t2,t3,dht1):
    httpget = {'field1': t1, 'field2': t2, 'field3': t3,'field4': dht1} #set raw json data
    r = requests.get(os.getenv("THINGSPEAK"), params = httpget) # http post

# 連線設定
# 初始化地程式
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("","")
client.connect('broker.mqttgo.io', 1883, 60)
client.loop_forever()