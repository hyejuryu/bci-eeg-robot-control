#include <Servo.h>

enum class ActuatorState {
  STOP,
  OPEN,
  CLOSE
};

struct TestStep {
  ActuatorState state;
  unsigned long durationMs;
  const char* label;
};

Servo gripperServo;

// Confirmed hardware configuration
const int SERVO_PIN = 9;

// Calibrated commanded-angle range
const int CLOSE_ANGLE_DEG = 60;
const int OPEN_ANGLE_DEG = 120;
const int STARTUP_ANGLE_DEG = 90;

// Motion policy
const int ANGLE_STEP_DEG = 2;
const unsigned long MOTION_UPDATE_INTERVAL_MS = 50;

// Use 3 for the first functional check.
// Change this to 10 for the final repeat test.
const int TEST_CYCLE_COUNT = 3;

/*
  Internal test sequence

  This sequence checks:
  - OPEN motion
  - direction reversal
  - STOP in the middle of the calibrated range
  - OPEN endpoint clamp
  - duplicate OPEN command
  - STOP during CLOSE
  - CLOSE endpoint clamp
*/
const TestStep TEST_STEPS[] = {
  {ActuatorState::STOP,  2000, "STARTUP_STOP"},
  {ActuatorState::OPEN,   400, "OPEN_START"},
  {ActuatorState::CLOSE,  300, "REVERSE_TO_CLOSE"},
  {ActuatorState::STOP,  1000, "STOP_MID_RANGE"},
  {ActuatorState::OPEN,  1000, "OPEN_TO_ENDPOINT"},
  {ActuatorState::OPEN,   400, "DUPLICATE_OPEN"},
  {ActuatorState::CLOSE,  700, "CLOSE_START"},
  {ActuatorState::STOP,  1000, "STOP_MID_CLOSE"},
  {ActuatorState::CLOSE, 1200, "CLOSE_TO_ENDPOINT"},
  {ActuatorState::STOP,  1500, "FINAL_STOP"}
};

const int TEST_STEP_COUNT =
  sizeof(TEST_STEPS) / sizeof(TEST_STEPS[0]);

ActuatorState currentState = ActuatorState::STOP;
int currentCommandedAngleDeg = STARTUP_ANGLE_DEG;

int currentStepIndex = 0;
int completedCycleCount = 0;

unsigned long stepStartMs = 0;
unsigned long lastMotionUpdateMs = 0;

bool testFinished = false;

const char* stateName(ActuatorState state) {
  switch (state) {
    case ActuatorState::OPEN:
      return "OPEN";

    case ActuatorState::CLOSE:
      return "CLOSE";

    case ActuatorState::STOP:
    default:
      return "STOP";
  }
}

void setActuatorState(
  ActuatorState requestedState,
  const char* stepLabel
) {
  Serial.print("Step: ");
  Serial.print(stepLabel);
  Serial.print(" | Requested state: ");
  Serial.print(stateName(requestedState));
  Serial.print(" | Commanded angle: ");
  Serial.println(currentCommandedAngleDeg);

  if (requestedState == currentState) {
    Serial.println(
      "Duplicate state: motion was not restarted."
    );
    return;
  }

  currentState = requestedState;
}

void updateActuatorMotion() {
  const unsigned long nowMs = millis();

  if (
    nowMs - lastMotionUpdateMs
    < MOTION_UPDATE_INTERVAL_MS
  ) {
    return;
  }

  lastMotionUpdateMs = nowMs;

  int nextAngleDeg = currentCommandedAngleDeg;

  if (currentState == ActuatorState::OPEN) {
    nextAngleDeg += ANGLE_STEP_DEG;

    if (nextAngleDeg > OPEN_ANGLE_DEG) {
      nextAngleDeg = OPEN_ANGLE_DEG;
    }
  }

  else if (currentState == ActuatorState::CLOSE) {
    nextAngleDeg -= ANGLE_STEP_DEG;

    if (nextAngleDeg < CLOSE_ANGLE_DEG) {
      nextAngleDeg = CLOSE_ANGLE_DEG;
    }
  }

  else {
    // STOP:
    // Keep the last commanded angle unchanged.
    return;
  }

  if (nextAngleDeg != currentCommandedAngleDeg) {
    currentCommandedAngleDeg = nextAngleDeg;
    gripperServo.write(currentCommandedAngleDeg);
  }
}

void startCurrentTestStep() {
  const TestStep& step = TEST_STEPS[currentStepIndex];

  setActuatorState(step.state, step.label);
  stepStartMs = millis();
}

void updateTestSequence() {
  if (testFinished) {
    return;
  }

  const TestStep& step = TEST_STEPS[currentStepIndex];

  if (millis() - stepStartMs < step.durationMs) {
    return;
  }

  currentStepIndex++;

  if (currentStepIndex >= TEST_STEP_COUNT) {
    completedCycleCount++;

    Serial.print("Completed cycle: ");
    Serial.println(completedCycleCount);

    if (completedCycleCount >= TEST_CYCLE_COUNT) {
      currentState = ActuatorState::STOP;
      testFinished = true;

      Serial.println("Test sequence finished.");
      Serial.print("Final commanded angle: ");
      Serial.println(currentCommandedAngleDeg);
      return;
    }

    currentStepIndex = 0;
  }

  startCurrentTestStep();
}

void setup() {
  Serial.begin(9600);

  /*
    The Servo library initially uses a pulse near its nominal
    center position when the servo is attached. The selected
    startup angle is also 90 degrees.
  */
  gripperServo.attach(SERVO_PIN);
  gripperServo.write(STARTUP_ANGLE_DEG);

  currentCommandedAngleDeg = STARTUP_ANGLE_DEG;
  currentState = ActuatorState::STOP;

  delay(500);

  Serial.println("Session 17 actuator test started.");
  Serial.println("OPEN endpoint: 120 deg");
  Serial.println("CLOSE endpoint: 60 deg");
  Serial.println("Startup angle: 90 deg");

  lastMotionUpdateMs = millis();
  startCurrentTestStep();
}

void loop() {
  updateActuatorMotion();
  updateTestSequence();
}