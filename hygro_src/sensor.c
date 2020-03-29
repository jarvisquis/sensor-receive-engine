// Includes
#include <RCSwitch.h>
#include "LowPower.h"

//Globals
#define DEBUG 1

#define HYGRO "3000"
#define VOLT "4000"
#define ERRORCODE "9999"
// Increment for each sensor
#define SOURCEADDR "100000"
#define PROJECTCODE "1000000"

// Config values
const int hygroPowerPin = 8;
const int rfPowerPin = 6;
const int rfPin = 7;
const int pinLed = 13;


const int timeToSleep = 600;
const int transmitRepeat = 10;

long nonce = 10000;

RCSwitch rf = RCSwitch();

void setup() {
  Serial.begin(9600);
  write_log("Init app");
  pinMode(hygroPowerPin, INPUT);
  pinMode(rfPowerPin, INPUT);

  pinMode(pinLed, OUTPUT);
  digitalWrite(pinLed, HIGH);
  delay(3000);
  digitalWrite(pinLed, LOW);
  pinMode(pinLed, INPUT);


}

void loop() {
  write_info(">>>Starting transmitter");
  pinMode(rfPowerPin, OUTPUT);
  digitalWrite(rfPowerPin, HIGH);
  rf.enableTransmit(rfPin);
  rf.setRepeatTransmit(transmitRepeat);

  write_info(">>>Volt");
  measure_batt_voltage();

  write_info(">>>Hygro");
  measure_hygro();

  write_info(">>>Stopping transmitter");
  rf.disableTransmit();
  digitalWrite(rfPowerPin, LOW);
  pinMode(rfPowerPin, INPUT);

  write_info(">>>Go to sleep");
  delay(500);
  sleep_seconds(timeToSleep);

}

void measure_batt_voltage() {
  write_log("Starting voltage calc");
  long result = 0;
  // Read 1.1V reference against AVcc
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(100); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Convert
  while (bit_is_set(ADCSRA,ADSC));
  result = ADCL;
  result |= ADCH<<8;
  result = 1126400L / result; // Back-calculate AVcc in mV
  write_log("Volt - " + String(result));
  send_data(result, atol(VOLT));
}

void measure_hygro() {
  write_log("Powering sensor");
  pinMode(hygroPowerPin, OUTPUT);
  digitalWrite(hygroPowerPin, HIGH);

  delay(500);

  int sensorValue = analogRead(A0);
  write_log("Sensor value - " + String(sensorValue));

  sensorValue = constrain(sensorValue, 300, 1023);
  int hygro = map(sensorValue, 0, 1023, 100, 0);

  write_log("Hygro - " + String(hygro));
  send_data(hygro, atol(HYGRO));

  write_log("Shutting sensor down");
  digitalWrite(hygroPowerPin, LOW);
  pinMode(hygroPowerPin, INPUT);
}
void send_data(long dataToSend, long dataType) {
  /*
      datagram: <PROJECTCODE><SOURCEADDR><NONCE><DATATYPE><VALUE>
      <NONCE> rolling counting from 10000 to 90000
  */
  long dataSum = atol(ERRORCODE);
  if (dataToSend == dataSum) {
    write_log("Got errorcode");
  } else {
    dataSum = dataToSend + dataType;
    write_log("Sending data - " + String(dataToSend) + " for type - " + String(dataType));
  }

  dataSum = dataSum + atol(PROJECTCODE) + atol(SOURCEADDR) + nonce;
  write_log("DataSum incl. Sourcecode: " + String(dataSum));

  rf.send(dataSum, 24);

  nonce = nonce + 10000;
  if (nonce >= 100000) {
    nonce = 10000;
  }
}

void write_info(String msg) {
  Serial.println("[INFO]: " + msg);
}
void write_log(String msg) {
  if (DEBUG == 1) {
    Serial.println("[DEBUG]: " + msg);
  }
}
void sleep_seconds(int seconds)
{
  for (int i = 0; i < seconds; i++) {
     LowPower.powerDown(SLEEP_1S, ADC_OFF, BOD_OFF);
  }
}