# Milestone 05 — Minimum Offline EEG-Derived Replay-Control Integration

## 1. Overview

Milestone 05 connected the frozen EEG-derived command artifacts from Milestone 04 to a minimum Arduino–servo–gripper control path.

Session 17 established and froze the actuator configuration supporting `OPEN`, `CLOSE`, and `STOP`. Session 18 replaced the Arduino-internal test sequence with a Python–Arduino serial interface and validated startup, command parsing, terminal responses, and host-side logging. Session 19 then replaced the validation-generated command source with the frozen decision-rule v0.1 stream from Session 16 and executed two source-linked stored-command replay runs.

The end-to-end pipeline was:

```text
posterior-alpha feature
→ decision rule v0.1
→ frozen command stream
→ replay-event selection and timing
→ serial command transmission and ACK
→ actuator movement
```

---

## 2. Period Covered

| Item               | Description                                    |
| ------------------ | ---------------------------------------------- |
| Milestone          | Milestone 05                                   |
| Sessions covered   | Sessions 17–20                                 |
| Actual work period | 2026-07-25 to 2026-08-08                       |
| Primary phase      | Offline EEG-derived replay-control integration |
| Final status       | Completed                                      |
| Next phase         | Parameter-sensitivity and robustness analysis  |

---

## 3. Sessions Covered

| Session    | Main focus                                | Main outcome                                                        |
| ---------- | ----------------------------------------- | ------------------------------------------------------------------- |
| Session 17 | Arduino–servo–gripper actuator validation | Frozen actuator-v0.1 configuration                                  |
| Session 18 | Python–Arduino serial communication       | Reusable serial protocol, client, ACK/ERR handling, and logs        |
| Session 19 | Stored EEG-derived command replay         | Source-linked `STOP → OPEN` and `STOP → CLOSE` replay demonstration |
| Session 20 | Integration review and milestone closure  | Cross-session consistency check and downstream baseline handoff     |

Session 20 served as an integration and milestone buffer for reviewing continuity across the actuator, serial, and replay layers.

---

## 4. Integration Context and Fixed Interfaces

### 4.1 Frozen EEG-Derived Input

The stored replay used the decision rule v0.1 artifacts frozen in Session 16.

```text
rule_id: thr-gap-mid__smooth-none__dwell-2
configuration: win-2s_step-1s
threshold: threshold_gap_midpoint
smoothing: smooth-none
dwell: 2 updates
```

The command-state mapping was:

```text
LOW_ALPHA   → CMD_OPEN
HIGH_ALPHA  → CMD_CLOSE
UNAVAILABLE → CMD_STOP
```

The frozen decision stream contained 118 rows:

```text
Subject 1, Run 1: 59 rows
Subject 1, Run 2: 59 rows
```

### 4.2 Actuator Configuration

The actuator-v0.1 configuration established in Session 17 was retained through Sessions 18–19.

| Item                     | Configuration                            |
| ------------------------ | ---------------------------------------- |
| Board                    | Arduino Uno R3-compatible board          |
| Servo                    | Tower Pro SG90, `S17-SERVO-A`            |
| Servo signal pin         | D9                                       |
| Servo power              | External 5 V, 2 A rail                   |
| Common ground            | Arduino GND connected to servo-power GND |
| CLOSE commanded endpoint | 60°                                      |
| Startup commanded angle  | 90°                                      |
| OPEN commanded endpoint  | 120°                                     |
| Motion update            | 2° every 50 ms                           |
| STOP                     | Stop further commanded-angle updates     |
| Endpoint behavior        | Clamp to the 60–120° commanded range     |

These values are commanded angles, not independently measured shaft angles.

### 4.3 Serial Interface

Session 18 defined `serial-protocol-v0.1`, which was reused without changing the transport contract during Session 19.

| Item               | Configuration                      |
| ------------------ | ---------------------------------- |
| Protocol version   | `S18_V0.1`                         |
| Baud rate          | 9600                               |
| Encoding           | ASCII                              |
| Commands           | `OPEN`, `CLOSE`, `STOP`            |
| Startup message    | `READY,S18_V0.1,STOP,90`           |
| Terminal responses | `ACK` or `ERR`                     |
| ACK results        | `APPLIED`, `DUPLICATE`, `REVERSED` |
| Command policy     | One unresolved command at a time   |
| Logging            | Host-side TX/RX event records      |

This interface allowed the command source to change from the Session 18 validation sequence to the frozen EEG-derived command stream without modifying the serial transport layer.

---

## 5. Key Technical Outcomes

### 5.1 Minimum Actuator-Control Baseline

Session 17 established a working servo-gripper configuration before serial control was introduced.

The validation covered:

* board upload and reset;
* external servo-power configuration;
* unloaded servo operation;
* gripper mechanical movement;
* endpoint calibration;
* `OPEN`, `CLOSE`, and `STOP`;
* duplicate-state handling;
* direction reversal; and
* endpoint clamping.

The selected 60–120° commanded range supported visible opening and closing movement without observed persistent stall, gear skip, out-of-range motion, or board reset during the recorded functional tests.

A brief repeatable displacement was observed during startup/reset and retained as a known actuator behavior.

### 5.2 Reusable Serial Command–Acknowledgement Interface

Session 18 replaced the Arduino-internal control sequence with Python-generated serial commands.

Two independent port-open validation runs were executed.

| Run   | Validation results | Event rows | TX | RX |
| ----- | -----------------: | ---------: | -: | -: |
| Run 1 |           6/6 PASS |         39 | 19 | 20 |
| Run 2 |           6/6 PASS |         39 | 19 | 20 |

Both runs received the expected startup message:

```text
READY,S18_V0.1,STOP,90
```

The validation covered:

* startup `READY`;
* invalid-command handling;
* `STOP` commanded-angle retention;
* direction reversal;
* OPEN endpoint reporting; and
* CLOSE endpoint reporting.

No command timeout or malformed response was recorded in either run.

The resulting `SerialClient` and protocol parser separated transport handling from command-generation logic and provided the reusable interface required for stored EEG-derived replay.

### 5.3 Source-Linked Replay-Event Construction

Session 19 loaded and validated the frozen 118-row command stream before hardware transmission.

Replay events were selected using:

```text
recording first row
+
subsequent command-state changes
```

This reduced the stored stream from 118 source rows to four transmitted events while preserving the initial command state and subsequent command transition for each recording.

| Source recording                        | Frozen rows | Replay events | Replay sequence |
| --------------------------------------- | ----------: | ------------: | --------------- |
| Subject 1, Run 1 — baseline eyes open   |          59 |             2 | `STOP → OPEN`   |
| Subject 1, Run 2 — baseline eyes closed |          59 |             2 | `STOP → CLOSE`  |

Each selected event retained its source recording, source window index, decision time, command state, and source-event identifier.

The command vocabulary was translated directly as:

```text
CMD_STOP  → STOP
CMD_OPEN  → OPEN
CMD_CLOSE → CLOSE
```

Each source recording used an independent replay clock and a fresh serial connection.

### 5.4 Integrated Source-to-Actuator Replay

The final integrated replay executed both recording plans using the Session 18 serial interface and Session 17 actuator configuration.

| Replay run     | Command sequence | Observed ACK sequence            | Result |
| -------------- | ---------------- | -------------------------------- | ------ |
| `S19-S001-R01` | `STOP → OPEN`    | `DUPLICATE/STOP → APPLIED/OPEN`  | PASS   |
| `S19-S001-R02` | `STOP → CLOSE`   | `DUPLICATE/STOP → APPLIED/CLOSE` | PASS   |

All four transmitted commands matched the expected ACK result and actuator mode.

The integrated run produced:

```text
4 transmitted replay events
4/4 event-level PASS

2 recording replay runs
2/2 recording-level PASS
```

Visual evidence recorded opening-direction gripper movement during Run 1 and closing-direction gripper movement during Run 2.

The source-linked event log and recording-level summary preserve the software execution record, while the terminal screenshot, OPEN/CLOSE frames, and integrated replay video document the corresponding demonstration.

### 5.5 Replay Timing and Saved-Output Validation

The final integrated replay produced the following host-side timing trace:

| Run   | Command | Schedule offset | ACK round-trip time |
| ----- | ------- | --------------: | ------------------: |
| Run 1 | `STOP`  |          +16 ms |               31 ms |
| Run 1 | `OPEN`  |            0 ms |               31 ms |
| Run 2 | `STOP`  |            0 ms |               47 ms |
| Run 2 | `CLOSE` |            0 ms |               31 ms |

All four ACK responses were received before the next 1.0 s replay target.

The final output files were saved and reloaded. Reload validation confirmed:

* four source-linked event rows;
* two recording-summary rows;
* four event-level PASS states;
* two recording-level PASS states; and
* matching source-event identities.

---

## 6. Integration Interpretation

Sessions 17–19 established a traceable offline replay-control path from the frozen EEG-derived command stream to observable gripper actuation without changing the previously selected actuator and serial interfaces.

Serial ACK records verified the software command response and reported actuator mode, while the video and image records documented visible gripper movement.

The observed 31–47 ms ACK round-trip times were below the 1.0 s replay interval, so the sequential ACK-before-next-command policy did not delay the tested replay schedule.

---

## 7. Decisions and Baselines for the Next Analysis Phase

### 7.1 Baseline Comparison Condition

The following configuration will serve as the baseline comparison condition for the next parameter-sensitivity analysis:

```text
Subject: 1
Runs: 1 and 2

Feature:
posterior_alpha_mean_psd

Window length:
2.0 s

Step size:
1.0 s

Decision rule:
thr-gap-mid__smooth-none__dwell-2

Threshold:
threshold_gap_midpoint
1.3987182661955795e-10 V²/Hz

Smoothing:
none

Dwell:
2 available updates
```

This configuration is a comparison baseline rather than a fixed final parameter set. Later analyses will vary window length, step size, threshold, smoothing, and dwell relative to this condition.

### 7.2 Replay-Control Baseline

The following replay procedure will be retained as the baseline execution procedure:

```text
event selection:
recording first row + command-state changes

replay timing:
source-relative timing
independent replay clock per recording

serial startup:
fresh connection per recording
READY validation before command transmission

transport:
S18_V0.1
9600 baud
one unresolved command at a time
terminal ACK or ERR before the next command

committed script default:
validation_only
```

Parameter sensitivity will first be evaluated offline by comparing the resulting feature streams and command streams. Hardware replay will remain a selected demonstration step rather than being repeated for every parameter configuration.

---

## 8. Canonical Outputs

### 8.1 Actuator Layer

* [`firmware/session-17/session17_actuator_control/session17_actuator_control.ino`](../firmware/session-17/session17_actuator_control/session17_actuator_control.ino)
* [`results/session-17/session17_actuator_config_v0.1.json`](../results/session-17/session17_actuator_config_v0.1.json)
* [`results/session-17/session17_actuator_validation.csv`](../results/session-17/session17_actuator_validation.csv)
* [`media/session-17/videos/s17_actuator_open_stop_close_v0.1.mp4`](../media/session-17/videos/s17_actuator_open_stop_close_v0.1.mp4)
* [`media/session-17/videos/s17_actuator_startup_reset_v0.1.mp4`](../media/session-17/videos/s17_actuator_startup_reset_v0.1.mp4)

### 8.2 Serial Layer

* [`firmware/session-18/session18_serial_actuator_control/session18_serial_actuator_control.ino`](../firmware/session-18/session18_serial_actuator_control/session18_serial_actuator_control.ino)
* [`src/bci_robot/serial_protocol.py`](../src/bci_robot/serial_protocol.py)
* [`src/bci_robot/serial_client.py`](../src/bci_robot/serial_client.py)
* [`scripts/12_s18_serial_controller.py`](../scripts/12_s18_serial_controller.py)
* [`results/session-18/session18_serial_protocol_v0.1.json`](../results/session-18/session18_serial_protocol_v0.1.json)
* [`results/session-18/session18_serial_validation_summary.csv`](../results/session-18/session18_serial_validation_summary.csv)
* [`results/session-18/session18_serial_event_log.csv`](../results/session-18/session18_serial_event_log.csv)
* [`media/session-18/screenshots/session18_python_serial_validation_v0.1.png`](../media/session-18/screenshots/session18_python_serial_validation_v0.1.png)
* [`media/session-18/videos/session18_python_serial_actuator_validation_v0.1.mp4`](../media/session-18/videos/session18_python_serial_actuator_validation_v0.1.mp4)

### 8.3 Replay Layer

* [`scripts/13_s19_stored_command_replay.py`](../scripts/13_s19_stored_command_replay.py)
* [`results/session-19/session19_source-linked_replay_event_log.csv`](../results/session-19/session19_source-linked_replay_event_log.csv)
* [`results/session-19/session19_recording_replay_summary.csv`](../results/session-19/session19_recording_replay_summary.csv)
* [`media/session-19/videos/session19_integrated_stored-command_replay_v0.1.mp4`](../media/session-19/videos/session19_integrated_stored-command_replay_v0.1.mp4)
* [`media/session-19/screenshots/session19_integrated_replay_terminal_pass.png`](../media/session-19/screenshots/session19_integrated_replay_terminal_pass.png)
* [`media/session-19/screenshots/session19_integrated_replay_open_frame.png`](../media/session-19/screenshots/session19_integrated_replay_open_frame.png)
* [`media/session-19/screenshots/session19_integrated_replay_close_frame.png`](../media/session-19/screenshots/session19_integrated_replay_close_frame.png)

### 8.4 Upstream Interface Artifacts

* [`results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json`](../results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json)
* [`results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1-stream.csv`](../results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1-stream.csv)

---

## 9. Open Questions and Remaining Uncertainties

1. How do window length, step size, threshold, smoothing, and dwell parameters change feature variability, command switching, initialization timing, and short command episodes?
2. How stable are the selected feature and command behaviors across additional recordings and subjects?
3. How often do feature values approach or cross the selected threshold, and how does this affect command stability?
4. What latency is added by processing and actuator motion beyond the measured host-side serial ACK round-trip time?
5. What contributes to the brief repeatable startup/reset displacement observed in the actuator configuration?

---

## 10. Next Phase

The next phase will return to analysis rather than extend the actuator hardware.

Session 21 will use the Milestone 05 baseline comparison condition to evaluate sensitivity to:

* window length;
* step size;
* threshold;
* smoothing; and
* dwell.

The analysis will examine how these parameter choices affect feature variability and command behavior before any additional replay condition is selected.

Later sessions will extend the analysis to additional recordings and subjects and examine threshold proximity, command switching, short command episodes, and latency components.

---

## 11. Milestone Reflection

Milestone 04 ended with a frozen EEG-derived command stream. Milestone 05 extended that result into a traceable offline actuator demonstration and established the integration baseline for subsequent parameter-sensitivity and robustness analyses.

---

## 12. Related Records

* [`reports/milestone-04-session-13-to-16.md`](milestone-04-session-13-to-16.md)
* [`weekly-notes/session-17-260725.md`](../weekly-notes/session-17-260725.md)
* [`weekly-notes/session-18-260801.md`](../weekly-notes/session-18-260801.md)
* [`weekly-notes/session-19-260804.md`](../weekly-notes/session-19-260804.md)
* [`docs/timeline-revision-2026-07-12.md`](../docs/timeline-revision-2026-07-12.md)
* [`results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json`](../results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json)
* [`results/session-19/session19_source-linked_replay_event_log.csv`](../results/session-19/session19_source-linked_replay_event_log.csv)
* [`results/session-19/session19_recording_replay_summary.csv`](../results/session-19/session19_recording_replay_summary.csv)
