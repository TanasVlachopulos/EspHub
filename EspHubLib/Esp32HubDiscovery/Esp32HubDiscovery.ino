#include "EspHubDiscovery.h"

#include <WiFi.h>
#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "SSD1306.h" // alias for `#include "SSD1306Wire.h"`

SSD1306  display(0x3c, 5, 4);


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

	handleWifiConnection();

	// init internal display
	display.init();
	display.setContrast(255);
	display.flipScreenVertically();

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
	while (!WiFi.smartConfigDone())
	{
		delay(500);
		Serial.printf(".");
	}
	Serial.printf("\nSmart config received, try to connect .");
	while (WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		Serial.printf(".");
	}
	Serial.printf("\nWiFi connected.\n");
}

void callback(char *topic, uint8_t *payload, unsigned int length)
{
	Serial.println("callback");
	// Serial.println(topic);
	// Serial.println((char *)payload);
	Serial.println(length);
	display.clear();

	char *buff;
	buff = (char *)malloc(length + 1);
	bzero(buff, length + 1);
	memcpy(buff, payload, length);


	display.drawXbm(32, 0, 64, 64, buff);
	display.display();

	// for (int i = 0; i < length; i++)
	// {
	// 	Serial.print((int)buff[i]);
	// }
	// Serial.println();
	free(buff);
}

/// Read internal temperature of ESP core
float getInternalTemperature()
{
	return (temprature_sens_read() - 32) / 1.8;
}
