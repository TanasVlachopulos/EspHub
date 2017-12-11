#include "FS.h"
#include "SPIFFS.h"


void setup() {
  Serial.begin(115200);
  if(!SPIFFS.begin())
  {
    Serial.println("SPIFFS Mount Failed");
    return;
  }
  else
  {
    Serial.println("SPIFFS mounted successfully");
  }
    
  // put your setup code here, to run once:
  File file = SPIFFS.open("/file", "w");
  if (!file)
    Serial.println("Cannot open file");
    
  uint8_t buffer[10] = "ahoj";
  file.write(buffer, sizeof(buffer));
  file.close();
  
}

void loop() {
  // put your main code here, to run repeatedly:
  File file = SPIFFS.open("/file", "r");
  if (!file)
    Serial.println("Cannot open file");
    
  uint8_t buffer[10];
  file.read(buffer, 10);
  Serial.printf("%s\n", buffer);
  file.close();
  delay(10000);
}
