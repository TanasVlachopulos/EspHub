#include "WiFi.h"

void setup() {
  Serial.begin(115200);
 

  //Init WiFi as Station, start SmartConfig
  WiFi.mode(WIFI_AP_STA);
  //Serial.println(WiFi.getAutoConnect());
  WiFi.beginSmartConfig();

  //Wait for SmartConfig packet from mobile
  Serial.println("Waiting for SmartConfig.");
  while (!WiFi.smartConfigDone()) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("SmartConfig received.");
//  Serial.printf("SSID: %s, Passwd: %s\n", WiFi.SSID(), WiFi.psk());
  

  //Wait for WiFi to connect to AP
  Serial.println("Waiting for WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println(WiFi.SSID());
  Serial.println(WiFi.BSSIDstr());
  Serial.println(WiFi.psk()); 

  Serial.println("WiFi Connected.");

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(WiFi.localIP());
  delay(10000);

}
