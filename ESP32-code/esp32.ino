
//宣告函式庫
#include <WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <SimpleDHT.h>
#include "EspMQTTClient.h"



char ssid[] = "PT";
char password[] = "qmui5953";

//溫度感測器
const int oneWireBus = 32;
const int oneWireBus2 = 33;
const int oneWireBus3 = 25;
const int potPin=5;
OneWire oneWire(oneWireBus);
OneWire oneWire2(oneWireBus2);
OneWire oneWire3(oneWireBus3);
DallasTemperature sensors(&oneWire);
DallasTemperature sensors2(&oneWire2);
DallasTemperature sensors3(&oneWire3);
int adventemp = 0;

//宣告DHT11 pin
int pinDHT22 = 4;
SimpleDHT22 dht22(pinDHT22);

//紅外線感測器
int humanPin=26;

//wifi 重連計時
unsigned long previousMillis = 0;
unsigned long interval = 30000;


//timer
int sec = 300;
int reboot = 0;

// Ph
float ph;
float Value=0;

//MQTT
EspMQTTClient client(
  "broker.MQTTGO.io",// MQTT Broker server ip
  1883, // MQTT Broker server ip
  "",
  "",
  "ESP32"// Client name that uniquely identify your device
);


void setup()    {

  pinMode(humanPin,INPUT);  
  Serial.begin(115200);
  Serial.print("開始連線到無線網路SSID:");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)   {

    Serial.print(".");
    delay(1000);
  }
  Serial.println("連線完成");
  sensors.begin();
  pinMode(potPin,INPUT);
}

void onConnectionEstablished() {
  client.publish("FOOD/temp", "MQTT連線成功");
  String temp = gettempmqtt();
  String boottemp = "{\"warn\":\"1\"," + temp;
  client.publish("FOOD/temp1", boottemp);
  Serial.println("MQTT連線成功");
}

void loop()   {
  client.loop(); //MQTT login
  //人體感測器
  int val=digitalRead(humanPin); //人體紅外線感測器讀出數位值
  if(val==HIGH&&sec%5==0) // 如果有人在移動
  { 
    client.publish("FOOD/temp1",  "{\"warn\":\"4\"}"); //人類感測器
  }
  unsigned long currentMillis = millis();
  if ((WiFi.status() != WL_CONNECTED) && (currentMillis - previousMillis >= interval))   {

    Serial.print(millis());
    Serial.println("Reconnecting to WiFi...");
    WiFi.disconnect();
    WifiConnect();
    previousMillis = currentMillis;

  }

  //宣告溫度計資料
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);
  sensors2.requestTemperatures();
  float temperatureC2 = sensors2.getTempCByIndex(0);
  sensors3.requestTemperatures();
  float temperatureC3 = sensors3.getTempCByIndex(0);
  int dhumidity = d22humidity();
  if (reboot == 144){
      ESP.restart();
  }
  if (sec == 300) {
      String tempmqtt = gettempmqtt();
      // 先換行再顯示
      String normaltemp = "{\"warn\":\"3\"," + tempmqtt;
      client.publish("FOOD/temp1", normaltemp);
      sec = 0;
      reboot = reboot + 1; 
  } else {
    adventemp = ((int)temperatureC + (int)temperatureC2 + (int)temperatureC3)/3;
    if ((int)adventemp >= 30 || (int)adventemp <= 20)    {
      stoptm();
    } else {
      sec = sec + 1;
      Serial.println(sec);
      delay(400);
    }
  }
}

//溫度超標
void stoptm()   {
  Serial.println(sec);
  if (sec % 30 == 0) {
    String tempmqtt = gethottemp();
    client.publish("FOOD/temp1", tempmqtt);
    sec = sec + 1;
    delay(1000);
  } else {
    sec = sec + 1;
  }
}


//獲取溫度
String gethottemp(){
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);
  sensors2.requestTemperatures();
  float temperatureC2 = sensors2.getTempCByIndex(0);
  sensors3.requestTemperatures();
  float temperatureC3 = sensors3.getTempCByIndex(0);
  int dhumidity = d22humidity();
  int ph= PHsenser();
  String temp = "{\"warn\":\"2\",\"temp1\":\"" + String(temperatureC) + "\",\"temp2\":\"" + String(temperatureC2) + "\",\"temp3\":\"" + String(temperatureC3) + "\",\"DHT22\":\"" + dhumidity +  "\",\"PH\":\"" + ph + "\"}";
  return temp;
}


//獲取mqtt用json溫度資料
String gettempmqtt(){
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);
  sensors2.requestTemperatures();
  float temperatureC2 = sensors2.getTempCByIndex(0);
  sensors3.requestTemperatures();
  float temperatureC3 = sensors3.getTempCByIndex(0);
  int dhumidity = d22humidity();
  int ph= PHsenser();
  String temp = "\"temp1\":\"" + String(temperatureC) + "\",\"temp2\":\"" + String(temperatureC2) + "\",\"temp3\":\"" + String(temperatureC3) + "\",\"DHT22\":\"" + dhumidity +  "\",\"PH\":\"" + ph + "\"}";
  return temp;
}

//d22濕度
int d22humidity(){
  byte temperature = 0;  byte humidity = 0;
  dht22.read(&temperature, &humidity, NULL);
  return (int)humidity;
}

//WiFi重連
void WifiConnect()    {

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)   {

    Serial.print(".");
    delay(1000);

  }
  client.publish("FOOD/temp1",  "{\"warn\":\"5\"}");
  sensors.begin();

}

int PHsenser(){
  Value= analogRead(potPin);
  float voltage=Value*(3.3/4095.0);
  ph=(3.3*voltage);
  return (int)ph;
}
