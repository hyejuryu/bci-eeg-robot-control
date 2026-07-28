#include <Servo.h>

Servo gripperServo;

const int SERVO_PIN = 9;
const int START_ANGLE_DEG = 90;

// 첫 시험에서는 실수로 0° 또는 180°를 보내지 못하도록
// 의도적으로 좁은 범위만 허용한다.
const int TEST_MIN_ANGLE_DEG = 60;
const int TEST_MAX_ANGLE_DEG = 120;

void setup() {
  Serial.begin(9600);

  gripperServo.attach(SERVO_PIN);
  gripperServo.write(START_ANGLE_DEG);
  delay(1000);

  Serial.println("Endpoint calibration ready.");
  Serial.println("Enter an angle from 60 to 120.");
}

void loop() {
  if (Serial.available() > 0) {
    const int requestedAngle = Serial.parseInt();

    // 남아 있는 newline 등의 문자를 비운다.
    while (Serial.available() > 0) {
      Serial.read();
    }

    if (
      requestedAngle >= TEST_MIN_ANGLE_DEG &&
      requestedAngle <= TEST_MAX_ANGLE_DEG
    ) {
      gripperServo.write(requestedAngle);

      Serial.print("Commanded angle: ");
      Serial.println(requestedAngle);
    } else {
      Serial.println("Rejected: enter an angle from 60 to 120.");
    }
  }
}