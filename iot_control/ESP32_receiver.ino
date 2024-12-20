#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = " "; // your wifi ssid
const char* password = " "; // your wifi password
const char* serverName = " ";  // your website address


void setup() {
    Serial.begin(115200); 
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting");
    }
    Serial.println("WIFI connected");
}

void loop() {

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http; 

        http.begin(serverName); 
        int httpResponseCode = http.GET(); 

        if (httpResponseCode > 0) {
            String payload = http.getString();

            StaticJsonDocument<1024> doc;
            DeserializationError error = deserializeJson(doc, payload);

            if (error) {
                Serial.println(error.c_str());
                return;
            }

            // Example ofjson format ：
            // {
            //   "state": "OK",
            //   "value": 123,
            //   "message": "Success"
            // }

            /////////////////////////////////////////////////////////////////////////
            // you can receive specific data here 
            // example:
            // int AC = doc[1]["Smart A/C"]; 
            // bool light1 = doc[1]["Smart Light A"];
            // // Serial.println(AC);
            /////////////////////////////////////////////////////////////////////////
        } else {
            Serial.println(httpResponseCode);
        }

        http.end();
    } else {
        Serial.println("WIFI X, try reconnecting");
        WiFi.begin(ssid, password);
        while (WiFi.status() != WL_CONNECTED) {
            delay(1000);
            Serial.println("reconnecting");
        }
        Serial.println("WIFI reconnected");
    }

    ///////////////////////////////////////////////////////////////
    // you can write your function like led
  
    ///////////////////////////////////////////////////////////////
    delay(10000);