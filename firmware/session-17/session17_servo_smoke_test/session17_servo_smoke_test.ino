#include <Servo.h>

Servo testServo;

const int SERVO_PIN = 9;
const int CENTER_ANGLE_DEG = 90;
const int LOW_TEST_ANGLE_DEG = 80;
const int HIGH_TEST_ANGLE_DEG = 100;
const int MOVE_WAIT_MS = 1500;
const int TEST_CYCLE_COUNT = 5;

void setup() {
  testServo.attach(SERVO_PIN);

  // Begin from the nominal center position.
  testServo.write(CENTER_ANGLE_DEG);
  delay(2000);

  // Move within a deliberately narrow range for the first test.
  for (int cycle = 0; cycle < TEST_CYCLE_COUNT; cycle++) {
    testServo.write(LOW_TEST_ANGLE_DEG);
    delay(MOVE_WAIT_MS);

    testServo.write(HIGH_TEST_ANGLE_DEG);
    delay(MOVE_WAIT_MS);
  }

  // Return to center and stop sending control pulses.
  testServo.write(CENTER_ANGLE_DEG);
  delay(1000);
  testServo.detach();
}

void loop() {
  // The smoke test runs once after power-up or reset.
}