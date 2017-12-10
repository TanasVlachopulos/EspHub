#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read();
#ifdef __cplusplus
}
#endif
uint8_t temprature_sens_read();

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.print("Temperature: ");
  
  // Convert raw temperature in F to Celsius degrees
  Serial.printf("temp: %d F\n", temprature_sens_read());
  Serial.print((temprature_sens_read() - 32) / 1.8);
  Serial.println(" C");
  Serial.printf("Hall: %d\n", hallRead());
  delay(5000);
}
