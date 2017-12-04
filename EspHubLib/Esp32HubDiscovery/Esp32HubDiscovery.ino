#include "EspHubDiscovery.h"
// #include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager

#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>

EspHubDiscovery hub("device_name");

// light sensor
// BH1750 lightMeter(0x23);

// Dallas DS18B20 DallasTemperature
// OneWire oneWire(D3);
// DallasTemperature DS18B20(&oneWire);

double timer = 0;

// LED and BUTTON demo
int lastButtonState = HIGH; // init on HIGH -> no click action after start
double btnPush;
int ledStatus = LOW;

void setup()
{
    Serial.begin(115200);

	// lightMeter.begin(BH1750_CONTINUOUS_HIGH_RES_MODE);

	// enable captive portal
	// WiFiManager wifiManager;
	// wifiManager.autoConnect("ESP_HUB_device"); // TODO customize captive portal

	hub.setCallback(callback);
	hub.setAbilities("['esp_test']");
    hub.begin();

	// init Dallas sensor
	// DS18B20.begin();

	// LED and BUTTON demo
	// pinMode(D6, OUTPUT); // set demo LED
	// pinMode(D0, OUTPUT); // set onboard LED
	// digitalWrite(D0, HIGH); // set onboard LED off
	// pinMode(D7, INPUT_PULLUP); // set demo button
	// btnPush = millis(); // prevent accidental button press after start
}

void loop()
{
    hub.loop();
	if (millis() - timer > 7000)
	{
		// hub.sendData("light", lightMeter.readLightLevel());
		// hub.sendData("DS18B20", getTemperature());
		hub.sendData("esp_test", "30");
		timer = millis();
	}

	// double pressTime = detectBtn(D7);
	
	// short button press under 5s 
	// if (pressTime > 0 && pressTime < 5000)
	// {
	// 	// switch LED status
	// 	if (ledStatus == LOW)
	// 	{
	// 		ledStatus = HIGH;
	// 		digitalWrite(D6, HIGH);
	// 		hub.sendData("switch", "on");
	// 	}
	// 	else
	// 	{
	// 		ledStatus = LOW;
	// 		digitalWrite(D6, LOW);
	// 		hub.sendData("switch", "off");
	// 	}
	// }
	// long button press more than 5s
	// else if (pressTime >= 5000)
	// {
	// 	// blink onboard LED
	// 	for (int i = 0; i < 3; i++)
	// 	{
	// 		digitalWrite(D0, LOW);
	// 		delay(150);
	// 		digitalWrite(D0, HIGH);
	// 		delay(150);
	// 	}
	// 	// reset device 
	// 	hub.clearEeprom();
	// 	WiFiManager wifiManager;
	// 	wifiManager.resetSettings();
	// 	ESP.restart();
	// }
}

void callback(char *topic, uint8_t *payload, unsigned int length)
{
	Serial.println(topic);
	StaticJsonBuffer<300> jsonBuffer;
	JsonObject& root = jsonBuffer.parseObject((char *)payload);

	if (!root.success())
	{
		Serial.println("JSON parsing fail!");
		return;
	}

	if (strcmp(topic, "esp_hub/device/8394748/data") == 0 && strcmp(root["value"], "on") == 0)
	{
		Serial.println("Switch ON");
		// digitalWrite(D6, HIGH);
		// ledStatus = HIGH;
	}
	else if (strcmp(topic, "esp_hub/device/8394748/data") == 0 && strcmp(root["value"], "off") == 0)
	{
		Serial.println("Switch OFF");
		// digitalWrite(D6, LOW);
		// ledStatus = LOW;
	}
}

// /// Detect button long press
// long detectBtn(int btnPin)
// {
// 	long pressTime = 0;
// 	long buttonState = digitalRead(btnPin);
// 	if (buttonState != lastButtonState)
// 	{
// 		if (buttonState == LOW)
// 		{
// 			btnPush = millis();
// 		}
// 		else
// 		{
// 			pressTime = millis() - btnPush;
// 		}
// 		delay(50);
// 	}
// 	lastButtonState = buttonState;
// 	return pressTime;
// }

// /// Read temperature from Dallas sensor
// float getTemperature() {
//   float temp;
//   do {
//     DS18B20.requestTemperatures(); 
//     temp = DS18B20.getTempCByIndex(0);
//     delay(100);
//   } while (temp == 85.0 || temp == (-127.0));
//   return temp;
// }