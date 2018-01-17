/*
#include "EspDisplaySSD1306.h"

SSD1306  _display(0x3c, 5, 4);

EspDisplaySSD1306::EspDisplaySSD1306(int address, int sda, int sdc)
{
	// display = new SSD1306(address, sda, sdc);
	_display.init();
	_display.setContrast(255);
	_display.flipScreenVertically();
}

EspDisplaySSD1306::EspDisplaySSD1306(SSD1306 *display)
{
	this.display = display;
}

void EspDisplaySSD1306::displayCallback(char *topic, uint8_t *payload, unsigned int length)
{
	Serial.println("callback");
	Serial.println(length);
	_display.clear();
	Serial.println("display clear");

	int16_t px = (int16_t)payload[length - 3];
	int16_t py = (int16_t)payload[length - 2];
	int16_t height = (int16_t)payload[length - 1];
	int16_t width = (int16_t)payload[length];
	Serial.println("var asigment");

	_display.drawXbm(px, px, width, height, (const char *)payload);
	Serial.println("draw");
	_display.display();
	Serial.println("display");
}
*/