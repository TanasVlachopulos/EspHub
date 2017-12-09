#include <MyPubSubClient.h>

//#ifdef MQTT_MAX_PACKET_SIZE
//#undef MQTT_MAX_PACKET_SIZE
#define MQTT_MAX_PACKET_SIZE 60
//#endif




uint64_t chipid;  

void setup() {
	Serial.begin(115200);
  PubSubClient();
}

void loop() {
	chipid=ESP.getEfuseMac();//The chip ID is essentially its MAC address(length: 6 bytes).
	Serial.printf("ESP32 Chip ID = %04X",(uint16_t)(chipid>>32));//print High 2 bytes
	Serial.printf("%08X\n",(uint32_t)chipid);//print Low 4bytes.

  int int_chipid = ESP.getEfuseMac();
  Serial.printf("int chip id: %d\n", int_chipid);

  Serial.printf("mem size %d\n", MQTT_MAX_PACKET_SIZE);
	delay(3000);

  

}
