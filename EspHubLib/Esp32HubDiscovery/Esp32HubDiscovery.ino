#include "EspHubDiscovery.h"

#include <WiFi.h>
#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// preapare reading internal temperature
#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read();
#ifdef __cplusplus
}
#endif
uint8_t temprature_sens_read();

#define MAIN_LOOP_INTERVAL 10000

EspHubDiscovery hub("ESP32_device");

double timer = 0;

void setup()
{
	Serial.begin(115200);

	EEPROM.begin(10);
	for (int i = 0; i < 10; i++)
	{
		Serial.print((char)EEPROM.read(i));
	}
	EEPROM.end();

	handleWifiConnection();

	hub.setCallback(callback);
	hub.setServer("192.168.1.1", 1883);
	hub.setAbilities("['internal_temp', 'hall_sensor']");
	hub.begin();

}

void loop()
{
	hub.loop();
	if (millis() - timer > MAIN_LOOP_INTERVAL)
	{
		hub.sendData("internal_temp", getInternalTemperature());
		hub.sendData("hall_sensor", hallRead());
		timer = millis();
	}

}

/// Connect to WiFi network using Smart Config
void handleWifiConnection()
{
	WiFi.mode(WIFI_AP_STA);
	WiFi.beginSmartConfig();

	Serial.printf("Waiting for Smart config setting from mobile app .");
	while(!WiFi.smartConfigDone())
	{
		delay(500);
		Serial.printf(".");
	}
	Serial.printf("\nSmart config received, try to connect .");
	while(WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		Serial.printf(".");
	}
	Serial.printf("\nWiFi connected.\n");
}

void callback(char *topic, uint8_t *payload, unsigned int length)
{
	Serial.println(topic);
	StaticJsonBuffer<300> jsonBuffer;
	JsonObject &root = jsonBuffer.parseObject((char *)payload);

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

/// Read internal temperature of ESP core
float getInternalTemperature()
{
	return (temprature_sens_read() - 32) / 1.8;
}
