#include "SSD1306.h" // alias for `#include "SSD1306Wire.h"`

#define I2C_ADDRESS_DISPLAY 0x3c
#define I2C_SDA_PIN 5
#define I2C_SDC_PIN 4

#define HEIGHT 64
#define WIDTH 128
// size of input buffer, 1 Byte = 8 px
#define BUFF_SIZE ((HEIGHT * WIDTH) / 8)

class EspDisplaySSD1306
{
  public:
	EspDisplaySSD1306(SSD1306 *display);
	EspDisplaySSD1306(int address, int sda, int sdc);
	void displayCallback(char *topic, uint8_t *payload, unsigned int length);

  private:
	SSD1306 *display;
};