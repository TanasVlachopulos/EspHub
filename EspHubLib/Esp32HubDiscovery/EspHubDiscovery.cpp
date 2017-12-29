#include "EspHubDiscovery.h"

Preferences preferences;

char server_ip[16] = {0};
int server_port = 1883; // server port - default 1883
long last_time = 0;		// time measurement variable

// Custom user defined callback function
std::function<void(char *, uint8_t *, unsigned int)> custom_callback;

// MQTT client
WiFiClient espClient;
PubSubClient client(espClient);
bool verified_to_server = false;

EspHubDiscovery::EspHubDiscovery(const char *deviceName)
{
	custom_callback = NULL;
	this->device_name = deviceName;
}

/// Initiating client function
/// check server from EEPROM and try connect in case of failure start discovery new server
void EspHubDiscovery::begin()
{
	if (readServerFromEeprom(server_ip, server_port) && this->checkServer(server_ip, server_port)) // check server stored in EEPROM
	{
		Serial.println("ESP_HUB: Connect to server with saved values");
		while (!verified_to_server) // wait DISCOVERY_INTERVAL seconds to server validation message
		{
			client.loop();
			yield();
			if (millis() - last_time > DISCOVERY_INTERVAL) // timeout validation interval -> start discovery new server
			{
				Serial.println("ESP_HUB: Validation of saved server timeout");
				Serial.println("ESP_HUB: Starting discovery ...");
				this->serverDiscovery();
				break;
			}
		}
	}
	else // no stored server in EEPROM or unvalid MQTT server -> start new discovery
	{
		Serial.println("ESP_HUB: Starting discovery ...");
		this->serverDiscovery();
	}

	client.setCallback(internalCallback); // set client Callback for handling server commands and user messages
	// set last_time to oposit of TELEMETRY_INTERVAL -> loop function send telemetry immediately after device start and begin function, otherwise we have to wait TELEMETRY_INTERVAL time after device start
	last_time = (-TELEMETRY_INTERVAL);
	Serial.println("ESP_HUB: Ready");
}

/// Handle Hub and MQTT events
/// Must be called in regular intervals, otherwise connect to MQTT broker will be lost
void EspHubDiscovery::loop()
{
	if (!client.connected())
	{
		Serial.println("ESP_HUB: unconnected during HUB loop");
		this->checkServer(server_ip, server_port);

		// TODO najit problem v teto sekci, ve chvili kdy dojde k pripojeni druheho esp k MQTT serveru, prvni ESP se odpoji a spedne do teto sekce
		// TODO je nutno zjistit, proc se sakra vsechna zarizeni odpoji od MQTT a castecne reseni by mohlo byt kdyby se zde nevolala uplne procedura check server, ale pouze obycejny reconect
	}
	client.loop();

	// send telemetry to server
	if (millis() - last_time > TELEMETRY_INTERVAL)
	{
		this->sendTelemetryData();
		last_time = millis();
	}
}

/// Notifi server about device abilities
/// Must be set before begin function
/// @param abilities in json array format (e.g.: "['temp', 'light', 'hum']")
void EspHubDiscovery::setAbilities(const char *abilities)
{
	this->abilities = abilities;
}


/// Manualy set MQTT server 
/// Must be set before begin function
/// @param ip IP address or domain name of MQTT server
/// @param port port number 
void EspHubDiscovery::setServer(const char *ip, int port)
{
	writeServerToEeprom(ip, port);
}

/// Send one value from sensor to server
/// @param type of outgoing data (e.g. temp, light, hum, ...)
/// @value measured value
void EspHubDiscovery::sendData(const char *type, const char *value)
{
	StaticJsonBuffer<JSON_SIZE> json_buffer;
	JsonObject &json = json_buffer.createObject();

	json["type"] = type;
	json["value"] = value;
	json["dvalue"] = 0;

	String msg;
	json.printTo(msg);

	Serial.print("ESP_HUB: Sending data ");
	Serial.println(type);
	this->sendJson(DATA_TOPIC, msg.c_str());
}

/// Send one value from sensor to server
/// @param type of outgoing data (e.g. temp, light, hum, ...)
/// @value measured value
void EspHubDiscovery::sendData(const char *type, const int value)
{
	StaticJsonBuffer<JSON_SIZE> json_buffer;
	JsonObject &json = json_buffer.createObject();

	json["type"] = type;
	json["value"] = value;
	json["dvalue"] = 0;

	String msg;
	json.printTo(msg);

	Serial.print("ESP_HUB: Sending data ");
	Serial.println(type);
	this->sendJson(DATA_TOPIC, msg.c_str());
}

/// Send one value from sensor to server
/// @param type of outgoing data (e.g. temp, light, hum, ...)
/// @value measured value
void EspHubDiscovery::sendData(const char *type, const float value)
{
	StaticJsonBuffer<JSON_SIZE> json_buffer;
	JsonObject &json = json_buffer.createObject();

	json["type"] = type;
	json["value"] = value;
	json["dvalue"] = 0;

	String msg;
	json.printTo(msg);

	Serial.print("ESP_HUB: Sending data ");
	Serial.println(type);
	this->sendJson(DATA_TOPIC, msg.c_str());
}

/// Send string to server with given topic header
/// @param topic_part last part of MQTT message topic - device identificator (esp_hub/device/<device_id>/) is predefined
/// @param json_str string in json format to send to the server
void EspHubDiscovery::sendJson(const char *topic_part, const char *json_str)
{
	String topic = MAIN_TOPIC;
	topic += (int)ESP.getEfuseMac();
	topic += "/";
	topic += topic_part;

	client.publish(topic.c_str(), json_str);
}

/// Clear EEPROM memory
void EspHubDiscovery::clearEeprom()
{
	preferences.begin("EspHub");
	preferences.clear();
	preferences.end();
}

void EspHubDiscovery::setCallback(std::function<void(char *, uint8_t *, unsigned int)> callback)
{
	custom_callback = callback;
}

/// Receive UDP broadcast until it found valid server
void EspHubDiscovery::serverDiscovery()
{
	WiFiUDP udp;
	udp.begin(UDP_LOCAL_PORT);
	int packet_size;
	// Serial.println("start listening");

	last_time = (-DISCOVERY_INTERVAL);

	do
	{
		packet_size = udp.parsePacket();
		if (packet_size)
		{
			// Serial.printf("Received %d bytes from %s, port %d\n", packet_size, udp.remoteIP().toString().c_str(), udp.remotePort());
			// get UDP msg from server
			char in_msg[UDP_MSG_SIZE] = {0};
			int msg_len = udp.read(in_msg, UDP_MSG_SIZE);
			if (msg_len > 0)
			{
				in_msg[msg_len] = 0;
			}

			// estimated size of json is 126 bytes (with server name < 30 characters)
			StaticJsonBuffer<2 * UDP_MSG_SIZE> json_buffer;
			JsonObject &json = json_buffer.parseObject((char *)in_msg);

			if (!json.success()) // handle unvalid JSON payload
			{
				continue;
			}

			Serial.printf("ESP_HUB: Candidate server: %s, IP: %s, port: %d\n", json["name"].as<char*>(), json["ip"].as<char*>(), json["port"].as<int>());

			long now = millis();
			if (now - last_time > DISCOVERY_INTERVAL) // discovery validation interval
			{
				// copy IP and port from UDP discovery to global variable - to verify "accept" msg from server
				strncpy(server_ip, json["ip"].as<char*>(), strlen(json["ip"].as<char*>()));
				server_port = json["port"].as<int>();

				this->checkServer(json["ip"].as<char*>(), json["port"].as<int>());
			}
		}

		if (client.connected()) // handle MQTT client events
		{
			client.loop();
		}
		yield();				   // handle WiFi events
	} while (!verified_to_server); // check global property verified_to_server
}

/// Try connect to MQTT server at ip and port, send Hello msg, set subscribe topic and set check Callback
/// @param ip server ip address
/// @param server port
/// @return true if connection success, false if connection failed
bool EspHubDiscovery::checkServer(const char *ip, int port)
{
	client.setServer(ip, port);

	if (!client.connected()) // try connect
	{
		Serial.print("ESP_HUB: Attempting MQTT connection ... ");
		String chipId = String((int)ESP.getEfuseMac());
		if (client.connect(chipId.c_str()))
		{
			client.setCallback(checkServerCallback);

			String topic = "esp_hub/device/";
			topic += (int)ESP.getEfuseMac();
			topic += "/#";
			client.subscribe(topic.c_str()); // subscribe device topic

			Serial.println("connected");
		}
		else
		{
			Serial.printf("failed (return code = %d). ", client.state());
			switch (client.state())
			{
				case -4:
					Serial.printf("The server did not respond within the keepalive time.\n");
					break;
				case -3:
					Serial.printf("The network connection was broken.\n");
					break;
				case -2:
					Serial.printf("The network conection was broken.\n");
					break;
				case -1:
					Serial.printf("The Client is disconnected cleanly.");
					break;
				case 1:
					Serial.printf("The server doesn't support the requested version of MQTT.\n");
					break;
				case 2:
					Serial.printf("The server rejected the client identifier.\n");
					break;
				case 3:
					Serial.printf("The server was unable to accept the connection.\n");
					break;
				case 4:
					Serial.printf("The username/password were rejected.\n");
					break;
				case 5:
					Serial.printf("The client was not authorized to connect.\n");
					break;
			}
		}
	}

	if (client.connected())
	{
		client.loop();

		// sending hello msg
		Serial.println("ESP_HUB: Sending hello message");
		char buff[JSON_SIZE] = {0};
		this->generateHelloMsg(buff, JSON_SIZE);
		client.publish("esp_hub/device/hello", buff);
		last_time = millis(); // for timer in discovery function
		return true;
	}

	return false;
}

/// Handle responses to Hello messages
/// Validate server responses with local server candidate or saved server
void EspHubDiscovery::checkServerCallback(char *topic, byte *payload, unsigned int length)
{
	String local_topic = "esp_hub/device/";
	local_topic += (int)ESP.getEfuseMac();
	local_topic += "/accept";

	if (strcmp(topic, local_topic.c_str()) == 0)
	{
		Serial.println("ESP_HUB: Callback accepted");

		StaticJsonBuffer<JSON_SIZE> json_buffer;
		JsonObject &json = json_buffer.parseObject((char *)payload);

		if (!json.success()) // handle unvalid JSON payload
		{
			return;
			Serial.println("ESP_HUB: JSON parse error");
		}

		// check server IP and port with data from UDP broadcast or data from EEPROM
		if (strcmp(json["ip"].as<char*>(), server_ip) == 0 && json["port"].as<int>() == server_port)
		{
			Serial.println("ESP_HUB: Server validated");

			// write to EEPROM
			writeServerToEeprom(json["ip"].as<char*>(), json["port"].as<int>());

			verified_to_server = true; // set global property verified_to_server
		}
		else
		{
			Serial.println("ESP_HUB: Server validation failed");
			client.disconnect(); // disconnect in case of ip addres mishmash
		}
	}
}

/// Create Hello message for this device
/// @param buff reference message buffer
/// @param buff_size size of buffer
void EspHubDiscovery::generateHelloMsg(char *buff, int buff_size)
{
	StaticJsonBuffer<JSON_SIZE> json_buffer;
	JsonObject &json = json_buffer.createObject();
	json["name"] = device_name;
	json["id"] = (int)ESP.getEfuseMac();
	json["ability"] = this->abilities;

	json.printTo(buff, buff_size);
}

/// Read stored server credentials from EEPROM
/// @param ip reference to server ip
/// @param port reference to server port
/// @return return false if no stored data
bool EspHubDiscovery::readServerFromEeprom(char *ip, int &port)
{
	Serial.println("ESP_HUB: Read from EEPROM");

	preferences.begin("EspHub");

	String stored_ip = preferences.getString("ip");
	strcpy(ip, stored_ip.c_str());
	port = preferences.getInt("port");

	preferences.end();

	return (ip == 0) ? false : true;
}

/// Write server credentials to EEPROM
/// @param ip server ip
/// @param port server port
void EspHubDiscovery::writeServerToEeprom(const char *ip, int port)
{
	Serial.println("ESP_HUB: Write to EEPROM");
	preferences.begin("EspHub");

	preferences.putString("ip", ip);
	preferences.putInt("port", port);

	preferences.end();
}

/// Callback for command topic from the server
/// Another topics redirect to user defined callback
/// @param topic MQTT message topic
/// @param payload of MQTT message
/// @param length of MQTT message
void EspHubDiscovery::internalCallback(char *topic, uint8_t *payload, unsigned int length)
{
	String topic_base = MAIN_TOPIC;
	topic_base += (int)ESP.getEfuseMac();
	topic_base += "/";

	String telemetry_topic = topic_base;
	telemetry_topic += TELEMETRY_TOPIC;

	String data_topic = topic_base;
	data_topic += DATA_TOPIC;

	String local_topic = topic_base;
	local_topic += CMD_TOPIC;

	// handle internal commands from server
	if (strcmp(topic, local_topic.c_str()) == 0)
	{
		Serial.println("ESP_HUB: command");
		// TODO implement command listening from server
	}
	// mute receiving loopback messages from Data and Telemetry topic
	if (strcmp(topic, telemetry_topic.c_str()) == 0 || strcmp(topic, data_topic.c_str()) == 0)
	{
		return;
	}
	else if (custom_callback != NULL)
	{
		custom_callback(topic, payload, length);
	}
}

/// Send telemetry data to server
void EspHubDiscovery::sendTelemetryData()
{
	StaticJsonBuffer<JSON_SIZE> json_buffer;
	JsonObject &json = json_buffer.createObject();

	char ssid[33];
	char ip[16];
	char mac[18];
	WiFi.SSID().toCharArray(ssid, 33);
	WiFi.localIP().toString().toCharArray(ip, 16);
	WiFi.macAddress().toCharArray(mac, 18);

	json["heap"] = ESP.getFreeHeap();
	json["real_f_size"] = ESP.getFlashChipSize();
	json["cycles"] = ESP.getCycleCount();
	json["rssi"] = WiFi.RSSI();
	json["ssid"] = ssid;
	json["local_ip"] = ip;
	json["mac"] = mac;

	String topic = MAIN_TOPIC;
	topic += (int)ESP.getEfuseMac();
	topic += "/";
	topic += TELEMETRY_TOPIC;
	String msg;
	json.printTo(msg);

	client.publish(topic.c_str(), msg.c_str());
	Serial.println("ESP_HUB: Sending telemetry ...");
}

/// Handle connection to WiFi network
/// Use stored credentials for connection to last known WiFi network.
/// If credential are invalid, network is unrecheable or connection cannot be established activate Smart config.
/// Smart config wait for response from application https://play.google.com/store/apps/details?id=com.cmmakerclub.iot.esptouch
/// If smart config successflully esptablish connection credentials are stored into memory
void EspHubDiscovery::handleWifiConnection()
{
	WiFi.mode(WIFI_AP_STA);
	preferences.begin("EspHub");

	String ssid = preferences.getString("ssid");
	String password = preferences.getString("psk");

	Serial.println("Try to connect with stored credentials.");
	WiFi.begin(ssid.c_str(), password.c_str());
	double startTime = millis();
	while((millis() < startTime + 20000) && (WiFi.status() != WL_CONNECTED))
	{
		delay(500);
		Serial.print(".");
	}

	// device is successfully connected
	if (WiFi.status() == WL_CONNECTED)
	{
		Serial.println("Successfully connected with stored credentials.");
		preferences.end();
		return;
	} 
	
	Serial.println("Cannot connect with stored credentials.");
	Serial.println("Starting smart config.");

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

	preferences.putString("ssid", WiFi.SSID());
	preferences.putString("psk", WiFi.psk());

	preferences.end();
}