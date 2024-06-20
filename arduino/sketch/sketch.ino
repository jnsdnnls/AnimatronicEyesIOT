#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Replace with your network credentials
const char* ssid = "raspi-IOT";
const char* password = "IoT_DeMo%24";

const char* mqtt_server = "10.3.141.1"; // MQTT broker IP address
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Create the PWM servo driver object
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      client.subscribe("joystick/data"); // Subscribe to the joystick data topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }

  Serial.println(messageTemp);

  // Parse the JSON payload
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, messageTemp);

  if (!error) {
  int x = doc["x"];
  int y = doc["y"];
  int trim = doc["eyeLids"];
  int switchval = doc["switch"];

  // Map input values to servo positions
  int servoXPos = map(x, -200, 200, 220, 440);
  int servoYPos = map(y, -200, 200, 250, 500); 
  int servoTrimPos = map(trim, 0, 100, -40, 40);

  int trimval = map(trim, 0, 1023, -40, 40);
  int uplidpulse = map(y, -200, 200, 440, 200);
  uplidpulse -= (trimval - 40);
  uplidpulse = constrain(uplidpulse, 200, 440);
  int altuplidpulse = 680 - uplidpulse;

  int lolidpulse = map(y, -200, 200, 380, 280);
  lolidpulse += (trimval / 2);
  lolidpulse = constrain(lolidpulse, 280, 370);
  int altlolidpulse = 680 - lolidpulse;
  
    // Set the servos based on the mapped values
    pwm.setPWM(0, 0, servoXPos); 
    pwm.setPWM(1, 0, servoYPos);

    if (switchval == 1) {
      pwm.setPWM(2, 0, 400);
      pwm.setPWM(3, 0, 240);
      pwm.setPWM(4, 0, 240);
      pwm.setPWM(5, 0, 400);

      delay(1000);
      pwm.setPWM(2, 0, uplidpulse);
      pwm.setPWM(3, 0, lolidpulse);
      pwm.setPWM(4, 0, altuplidpulse);
      pwm.setPWM(5, 0, altlolidpulse);

    } else {
      pwm.setPWM(2, 0, uplidpulse);
      pwm.setPWM(3, 0, lolidpulse);
      pwm.setPWM(4, 0, altuplidpulse);
      pwm.setPWM(5, 0, altlolidpulse);
    }


    Serial.print("left up lid: ");
    Serial.println(uplidpulse);
    Serial.print("left down lid: ");
    Serial.println(lolidpulse);
  } else {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Initialize the PWM servo driver
  pwm.begin();
  pwm.setPWMFreq(60);  // Analog servos run at ~60 Hz updates

  // Wait for driver to be ready
  delay(10);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
