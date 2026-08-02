#include <Servo.h>
#include <string.h>

enum class ActuatorState {
  STOP,
  OPEN,
  CLOSE
};

enum class CommandResult {
  APPLIED,
  DUPLICATE,
  REVERSED
};

Servo gripperServo;

// Confirmed hardware configuration
const int SERVO_PIN = 9;
const char* PROTOCOL_VERSION = "S18_V0.1";
const size_t SERIAL_INPUT_BUFFER_SIZE = 32;

// Calibrated commanded-angle range
const int CLOSE_ANGLE_DEG = 60;
const int OPEN_ANGLE_DEG = 120;
const int STARTUP_ANGLE_DEG = 90;

// Motion policy
const int ANGLE_STEP_DEG = 2;
const unsigned long MOTION_UPDATE_INTERVAL_MS = 50;

ActuatorState currentState = ActuatorState::STOP;
int currentCommandedAngleDeg = STARTUP_ANGLE_DEG;

unsigned long lastMotionUpdateMs = 0;

char serialInputBuffer[SERIAL_INPUT_BUFFER_SIZE] = {0};
size_t serialInputLength = 0;
bool serialInputOverflow = false;

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

const char* resultName(CommandResult result) {
  switch (result) {
    case CommandResult::DUPLICATE:
      return "DUPLICATE";

    case CommandResult::REVERSED:
      return "REVERSED";

    case CommandResult::APPLIED:
    default:
      return "APPLIED";
  }
}

void sendReady() {
  Serial.print("READY,");
  Serial.print(PROTOCOL_VERSION);
  Serial.print(",");
  Serial.print(stateName(currentState));
  Serial.print(",");
  Serial.println(currentCommandedAngleDeg);
}

void sendAck(
  ActuatorState requestedState,
  CommandResult result
) {
  Serial.print("ACK,");
  Serial.print(stateName(requestedState));
  Serial.print(",");
  Serial.print(resultName(result));
  Serial.print(",");
  Serial.print(stateName(currentState));
  Serial.print(",");
  Serial.println(currentCommandedAngleDeg);
}

void sendInvalidCommandError() {
  Serial.print("ERR,INVALID_COMMAND,");
  Serial.print(stateName(currentState));
  Serial.print(",");
  Serial.println(currentCommandedAngleDeg);
}

void resetSerialInputBuffer() {
  serialInputLength = 0;
  serialInputOverflow = false;
  serialInputBuffer[0] = '\0';
}

void trimSerialInputBuffer() {
  size_t startIndex = 0;

  while (
    startIndex < serialInputLength
    && (
      serialInputBuffer[startIndex] == ' '
      || serialInputBuffer[startIndex] == '\t'
    )
  ) {
    startIndex++;
  }

  size_t endIndex = serialInputLength;

  while (
    endIndex > startIndex
    && (
      serialInputBuffer[endIndex - 1] == ' '
      || serialInputBuffer[endIndex - 1] == '\t'
    )
  ) {
    endIndex--;
  }

  const size_t trimmedLength = endIndex - startIndex;

  if (startIndex > 0 && trimmedLength > 0) {
    memmove(
      serialInputBuffer,
      serialInputBuffer + startIndex,
      trimmedLength
    );
  }

  serialInputBuffer[trimmedLength] = '\0';
  serialInputLength = trimmedLength;
}

bool readSerialLine() {
  while (Serial.available() > 0) {
    const char incomingChar = Serial.read();

    if (incomingChar == '\r') {
      continue;
    }

    if (incomingChar == '\n') {
      if (serialInputOverflow) {
        sendInvalidCommandError();
        resetSerialInputBuffer();
        return false;
      }

      if (serialInputLength == 0) {
        resetSerialInputBuffer();
        return false;
      }

      serialInputBuffer[serialInputLength] = '\0';
      return true;
    }

    if (serialInputLength < SERIAL_INPUT_BUFFER_SIZE - 1) {
      serialInputBuffer[serialInputLength] = incomingChar;
      serialInputLength++;
    } else {
      serialInputOverflow = true;
    }
  }

  return false;
}

void processSerialCommand() {
  ActuatorState requestedState;

  if (strcmp(serialInputBuffer, "OPEN") == 0) {
    requestedState = ActuatorState::OPEN;
  } else if (strcmp(serialInputBuffer, "CLOSE") == 0) {
    requestedState = ActuatorState::CLOSE;
  } else if (strcmp(serialInputBuffer, "STOP") == 0) {
    requestedState = ActuatorState::STOP;
  } else {
    sendInvalidCommandError();
    return;
  }

  const CommandResult result =
    setActuatorState(requestedState);

  sendAck(requestedState, result);
}

CommandResult setActuatorState(
  ActuatorState requestedState
) {
  if (requestedState == currentState) {
    return CommandResult::DUPLICATE;
  }

  const bool isDirectionReversal =
    (
      currentState == ActuatorState::OPEN
      && requestedState == ActuatorState::CLOSE
    )
    ||
    (
      currentState == ActuatorState::CLOSE
      && requestedState == ActuatorState::OPEN
    );

  currentState = requestedState;

  if (isDirectionReversal) {
    return CommandResult::REVERSED;
  }

  return CommandResult::APPLIED;
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

  sendReady();

  lastMotionUpdateMs = millis();
}

void loop() {
  if (readSerialLine()) {
    trimSerialInputBuffer();

    if (serialInputLength > 0) {
      processSerialCommand();
    }

    resetSerialInputBuffer();
  }

  updateActuatorMotion();
}