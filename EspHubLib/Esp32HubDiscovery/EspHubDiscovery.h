// #include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino
// #include "WiFi.h"
// #include <DNSServer.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiClient.h>

// #include <ESP8266WebServer.h>

#include <EEPROM.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <MyPubSubClient.h>

#define EEPROM_SIZE 35			 // size of aloceted EEPROM memory
#define EEPROM_VARIABLES 2		 // count of JSON variables stored to EEPROM
#define JSON_SIZE 400			 // standard size of JSON buffer
#define UDP_MSG_SIZE 100		 // size of input UDP discovery broadcast
#define UDP_LOCAL_PORT 11114	 // UDP discovery port
#define DISCOVERY_INTERVAL 15000 // server discovery timeout
#define TELEMETRY_INTERVAL 30000 // sending telemetry data interval

// topic names
#define MAIN_TOPIC "esp_hub/device/"
#define DATA_TOPIC "data"
#define TELEMETRY_TOPIC "telemetry"
#define CMD_TOPIC "cmd"

class EspHubDiscovery
{
  public:
	EspHubDiscovery(const char *deviceName);
	void begin();
	void loop();
	void setAbilities(const char *abilities);
	void setServer(const char *ip, int port);
	void sendData(const char *type, const char *value);
	void sendData(const char *type, const int value);
	void sendData(const char *type, const float value);
	void sendJson(const char *topic_part, const char *json_str);
	void clearEeprom();
	void setCallback(std::function<void(char *, uint8_t *, unsigned int)> callback);

  private:
	void serverDiscovery();
	bool checkServer(const char *ip, int port);
	void static checkServerCallback(char *topic, byte *payload, unsigned int length);
	void generateHelloMsg(char *buff, int buff_size);
	bool static readServerFromEeprom(char *ip, int &port);
	void static writeServerToEeprom(const char *ip, int port);
	void static internalCallback(char *topic, uint8_t *payload, unsigned int length);
	void sendTelemetryData();
	const char *abilities;
	const char *device_name;
};