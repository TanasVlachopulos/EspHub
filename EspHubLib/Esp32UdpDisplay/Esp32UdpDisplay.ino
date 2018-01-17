#include "EspHubDiscovery.h"
#include <WiFi.h>
#include "SSD1306.h" // alias for `#include "SSD1306Wire.h"`
#include <WiFiUdp.h>

SSD1306  display(0x3c, 5, 4);
WiFiUDP udp;

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
#define UDP_PORT 9999 // listen on this port for incoming UDP connections
#define BUFF_SIZE 516 // size of incoming buffer in bytes

EspHubDiscovery hub("ESP32_device");

double timer = 0;
int packet_size = 0;
char payload[BUFF_SIZE];

void setup()
{
	Serial.begin(115200);

	// init internal display
	display.init();
	display.setContrast(255);
	display.flipScreenVertically();

	hub.handleWifiConnection();
	hub.setCallback(callback);
	hub.setServer("193.179.108.146", 1883);
	hub.setAbilities("['internal_temp', 'hall_sensor']");
	hub.begin();

	udp.begin(UDP_PORT);
}

void loop()
{
	hub.loop();
	if (millis() - timer > MAIN_LOOP_INTERVAL)
	// {
	// 	hub.sendData("internal_temp", getInternalTemperature());
	// 	hub.sendData("hall_sensor", hallRead());
	// 	timer = millis();
	// }
	packet_size = udp.parsePacket();
	if (packet_size > 0 && packet_size <= BUFF_SIZE)
	{
		// Serial.printf("Incoming UDP packet of size %d B.\n", packet_size);
		display.clear();

		udp.read(payload, packet_size);

		int16_t px = (int16_t)payload[packet_size - 4];
		int16_t py = (int16_t)payload[packet_size - 3];
		int16_t height = (int16_t)payload[packet_size - 2];
		int16_t width = (int16_t)payload[packet_size - 1];
		// Serial.printf("%d, %d, %d %d\n", px, py, height, width);

		display.drawXbm(px, py, width, height, (const char*)payload);
		display.display();
	}
	else if (packet_size > BUFF_SIZE)
	{
		Serial.printf("UDP buffer overflow. Incoming UDP packet (%d B) is larger than input buffer (%d B).\n", packet_size, BUFF_SIZE);
	}
}

void callback(char *topic, uint8_t *payload, unsigned int length)
{
}

/// Read internal temperature of ESP core
float getInternalTemperature()
{
	return (temprature_sens_read() - 32) / 1.8;
}
