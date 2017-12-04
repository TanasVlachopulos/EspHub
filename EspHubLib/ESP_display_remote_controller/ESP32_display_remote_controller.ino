/*
* Recieve bitmap line by line from MQTT server and draw it on ILI9341 display
*/
#include <ESP8266WiFi.h>
#include <MyPubSubClient.h>
#include <Adafruit_GFX.h>     // Core graphics library
#include "Adafruit_ILI9341.h" // Hardware-specific library
#include <SPI.h>
#include <OneWire.h>
#include <DallasTemperature.h> // handle temperature sensor
#include <ArduinoJson.h>
#include <Fonts/FreeMono12pt7b.h>
#include <Fonts/FreeSans12pt7b.h>
#include <Fonts/FreeSerif12pt7b.h>
#include "control_panel.h"	// Include local constants and defines 

// display settings
#define TFT_DC 5
#define TFT_CS 4
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);
uint16_t globalColor = ILI9341_BLUE;

// *** Bitmap parameters ***
int dispWidth;  // physical display width in pix
int dispHeight; // physical display heitht in pix
uint16_t x = 0;  // start x position
uint16_t y = 0;  // start y position
int bmpWidth = -1;
int bmpHeight = -1;
uint8_t bmpDepth = 24;  // color depth - only 24 bit is allowed
uint8_t lineDense = 0; // count of lines in one mqtt message
uint8_t r, g, b;
long bitmap_part = -1; // identify part of recieve bitmap, -1 means no information about part
// *** End bitmap parameters ***

// temperature sensor params
#define DALLAS_PIN D1
OneWire oneWire(DALLAS_PIN);
DallasTemperature DS18B20(&oneWire);

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char charPayload[255] = {0}; // input char from mqtt server

void setup()
{
    pinMode(BUILTIN_LED, OUTPUT); // Initialize the BUILTIN_LED pin as an output
    Serial.begin(115200);
    Serial.println();

    // init temperature sensor
    DS18B20.begin();

    // TFT settings
    tft.begin();
    tft.fillScreen(ILI9341_BLUE);
    dispWidth = tft.width();
    dispHeight = tft.height();
    Serial.print("display width, height: ");
    Serial.println(dispWidth);
    Serial.println(dispHeight);

    if ((x >= dispWidth) || (y >= dispHeight))
        Serial.println("Bad start position");

    // Set TFT address window to clipped image bounds
    tft.setAddrWindow(x, y, x + dispWidth - 1, y + dispHeight - 1);

    // Connection setting
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
}


// *** Draw bitmap ***
void bmpDraw(byte *row_data)
{
    int buffix = 0;
    uint8_t *data = (uint8_t *)row_data;
    // verifi if bitmap has corect dimension, bit depth and at least 1 line
    if (bmpDepth == 24 && lineDense > 0)
    {
        for (int col = 0; col < (bmpWidth * lineDense); col++)
        {
            r = data[buffix++];
            g = data[buffix++];
            b = data[buffix++];

            // push lines to display
            tft.pushColor(tft.color565(r, g, b));
        }
    }
    else
    {
        Serial.println("Bad input parameter.");
    }
    yield();
}

void fillScreen(uint8_t r, uint8_t g, uint8_t b) 
{
	tft.fillScreen(tft.color565(r, g, b));
	yield();
}

void drawText(uint16_t x, uint16_t y, uint8_t textSize, const char *text)
{
	tft.setCursor(x, y);
	tft.setTextColor(globalColor);
	tft.setTextSize(textSize);
	tft.println(text);
	yield();
}

void setColor(uint8_t r, uint8_t g, uint8_t b) 
{
	globalColor = tft.color565(r, g, b);
}

// *************************************************
// ************* Recieve data callback *************
//**************************************************
void callback(char *topic, byte *payload, unsigned int length)
{
    if (strcmp(topic, topic_data) == 0)
    {
		Serial.println(bitmap_part);
        bmpDraw(payload);
		return;
    }

	StaticJsonBuffer<300> jsonBuffer;
	JsonObject& root = jsonBuffer.parseObject((char *)payload);

	if (!root.success())
	{
		debugPrint("JSON parsing fail!");
		return;
	}

    // recieve number of bitmap part
    if (strcmp(topic, topic_part) == 0)
    {
        bitmap_part = root["part"].as<long>();
        if (bitmap_part == 0)
        {
            // reset img window when new bitmap arrive
            // tft.setAddrWindow(x, y, x + 50 - 1, y + 50 - 1);
            tft.setAddrWindow(x, y, x + bmpWidth - 1, y + bmpHeight - 1);			
        }
    }
    // recieve bitmap line density
    else if (strcmp(topic, topic_lineDense) == 0)
    {
        lineDense = root["dense"].as<uint8_t>();
        debugPrint(lineDense);
    }
    else if (strcmp(topic, topic_dimension) == 0)
    {
        bmpWidth = root["w"].as<int>();
        bmpHeight = root["h"].as<int>();
		x = root["x"].as<uint16_t>();
		y = root["y"].as<uint16_t>();
    }
	else if (strcmp(topic, "test/bitmap/fillScreen") == 0)
	{
		fillScreen(root["r"].as<uint8_t>(), root["g"].as<uint8_t>(), root["b"].as<uint8_t>());
	}
	else if (strcmp(topic, "test/bitmap/drawText") == 0)
	{
		drawText(root["x"].as<uint16_t>(), root["y"].as<uint16_t>(), root["textSize"].as<uint8_t>(), root["text"].asString());
	}
	else if (strcmp(topic, "test/bitmap/setColor") == 0)
	{
		setColor(root["r"].as<uint8_t>(), root["g"].as<uint8_t>(), root["b"].as<uint8_t>());
	}
	else if (strcmp(topic, "test/bitmap/drawLine") == 0)
	{
		tft.drawLine(root["x1"].as<int16_t>(), root["y1"].as<int16_t>(), root["x2"].as<int16_t>(), root["y2"].as<int16_t>(), globalColor);
	}
	else if (strcmp(topic, "test/bitmap/drawRect") == 0)
	{
		tft.drawRect(root["x"].as<int16_t>(), root["y"].as<int16_t>(), root["w"].as<int16_t>(), root["h"].as<int16_t>(), globalColor);
	}
	else if (strcmp(topic, "test/bitmap/drawFillRect") == 0)
	{
		tft.fillRect(root["x"].as<int16_t>(), root["y"].as<int16_t>(), root["w"].as<int16_t>(), root["h"].as<int16_t>(), globalColor);
	}
	else if (strcmp(topic, "test/bitmap/drawCircle") == 0)
	{
		tft.drawCircle(root["x"].as<int16_t>(), root["y"].as<int16_t>(), root["r"].as<int16_t>(), globalColor);
	}
	else if (strcmp(topic, "test/bitmap/drawFillCircle") == 0)
	{
		tft.fillCircle(root["x"].as<int16_t>(), root["y"].as<int16_t>(), root["r"].as<int16_t>(), globalColor);		
	}
	else if (strcmp(topic, "test/bitmap/drawRoundRect") == 0)
	{
		tft.drawRoundRect(root["x"].as<int16_t>(), root["y"].as<int16_t>(), root["w"].as<int16_t>(), root["h"].as<int16_t>(), root["r"].as<int16_t>(), globalColor);
	}
	else if (strcmp(topic, "test/bitmap/drawFillRoundRect") == 0)
	{
		tft.fillRoundRect(root["x"].as<int16_t>(), root["y"].as<int16_t>(), root["w"].as<int16_t>(), root["h"].as<int16_t>(), root["r"].as<int16_t>(), globalColor);
	}
	else if (strcmp(topic, "test/bitmap/setRotation") == 0)
	{
		tft.setRotation(root["rotation"].as<int8_t>());
	}
	else if (strcmp(topic, "test/bitmap/setFont") == 0)
	{
		const char *fontName = root["font"].asString();
		if (strcmp(fontName, "freeMono") == 0)
		{
			tft.setFont(&FreeMono12pt7b);
		}
		else if (strcmp(fontName, "freeSans") == 0)
		{
			tft.setFont(&FreeSans12pt7b);			
		}
		else if (strcmp(fontName, "freeSerif") == 0)
		{
			tft.setFont(&FreeSerif12pt7b);			
		}
		else
		{
			tft.setFont();
		}
	}
    else
    {
        Serial.println("unrecognizable MQTT tag");
    }

    yield();
}

void reconnect()
{
    // Loop until we're reconnected
    while (!client.connected())
    {
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect
        if (client.connect("ESP8266Client"))
        {
            Serial.println("connected");

            // subscribe bitmap topic
            client.subscribe("test/bitmap/#");
            // client.subscribe(topic_part);
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            // Wait 5 seconds before retrying
            delay(5000);
        }
    }
}

void setup_wifi()
{

    delay(10);
    // We start by connecting to a WiFi network
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void debugPrint(const char *msg)
{
    if (debug)
        Serial.println(msg);
}

void debugPrint(int msg)
{
    if (debug)
        Serial.println(msg);
}

float getTemperature() {
  float temp;
  do {
    DS18B20.requestTemperatures(); 
    temp = DS18B20.getTempCByIndex(0);
    delay(100);
    yield();
  } while (temp == 85.0 || temp == (-127.0));
  return temp;
}


void loop()
{

    if (!client.connected())
    {
        reconnect();
    }
    client.loop();

    long now = millis();
    if (now - lastMsg > 5000)
    {
        StaticJsonBuffer<50> jsonBuffer;
        JsonObject &root = jsonBuffer.createObject();
        float temp = getTemperature();
        char tempStr[50];
        root["temp"] = temp;
        root.printTo(tempStr, sizeof(tempStr));
        // dtostrf(temp, 2, 2, tempStr);

        Serial.println("Send data to MQTT");
        Serial.println(tempStr);
        client.publish("client/test", tempStr);
    }
}
