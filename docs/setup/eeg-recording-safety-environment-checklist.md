# EEG Recording Safety and Environment Checklist v0.1

## Document metadata

- Created in: Session 09
- Used from: Session 10 onward

## 1. Purpose

This document defines the basic safety and environment checklist for future OpenBCI Cyton EEG recording sessions.

The goal is to reduce avoidable safety risks, recording artifacts, and setup ambiguity before collecting self-recorded EEG data.

## 2. Scope

This checklist applies to early OpenBCI EEG setup and recording sessions using:

- electrodes
- OpenBCI Cyton board
- USB dongle
- OpenBCI GUI
- short self-recorded EEG data collection

This includes:

- OpenBCI GUI connection test
- real-time waveform check
- eyes-open / eyes-closed alpha reactivity recording
- basic recording metadata collection

This checklist does not cover Arduino, servo motor, or robot control hardware.  
Those systems require a separate safety and setup checklist later and should remain electrically separate from the body-connected EEG setup at this stage.

## 3. Power and electrical safety

- Use battery power only for the Cyton board during body-connected recording.
- Do not charge the battery while the Cyton board is connected to the body.
- Do not connect Arduino, servo motors, robot hardware, or external powered circuits to the Cyton board during EEG recording.
- Do not modify the Cyton board, electrode cables, battery connector, or USB dongle during recording.
- Stop the session immediately if there is discomfort, pain, skin irritation, dizziness, anxiety, or unusual heat from any device.
- The first tests should be short and self-recorded only.

## 4. Physical setup

- Use a quiet room.
- Use a clean and stable desk.
- Use a non-rolling chair.
- Sit in a stable posture.
- Keep head, jaw, neck, facial muscles, and body movement minimal during recording.
- Keep unnecessary electronics away from the electrodes and cables.
- Keep phone chargers, power adapters, and unused devices away from the recording area.
- Route cables so they do not pull the headband or touch moving objects.
- Avoid fan or air-conditioner airflow directly moving the cables or headband.

## 5. Electrode and headband setup

- Check that the headband is stable before recording.
- Check that posterior electrodes are placed consistently with the montage document.
- Use comb electrodes for hair-covered posterior positions.
- Use earclip electrodes for the initial SRB2 reference and BIAS candidates.
- Check that earclips are attached firmly but comfortably.
- Stop and readjust if the headband moves, electrodes feel unstable, or cables pull on the setup.

## 6. Recording quality checks before data collection

Before saving any experimental data, check:

- Whether the intended channels are visible in the OpenBCI GUI.
- Whether unused channels are clearly disabled or ignored.
- Whether the waveform is not flat.
- Whether the waveform is not saturated.
- Whether large movement artifacts are visible.
- Whether electrode contact appears stable enough for a short test.
- Whether the recording file location is known.

## 7. Session metadata to record

Before or immediately after each recording session, record:

- Date
- Session number
- Subject: self-recording
- Room condition
- Chair and posture condition
- Cyton power source
- Active channel mapping
- SRB2 reference position
- BIAS position
- Electrode types used
- Recording duration
- Condition labels
- Any visible noise, movement, discomfort, or setup issue

## 8. Stop criteria

Stop the recording if:

- Any physical discomfort occurs.
- The headband or electrodes become unstable.
- The battery, board, or cables behave unexpectedly.
- The signal is clearly unusable due to movement or contact failure.
- The setup requires connecting external powered hardware to the EEG system.

## 9. Current decision

For early OpenBCI EEG sessions, the EEG setup will remain simple and isolated.

Initial rule:

```text
Cyton battery-powered EEG recording only
No Arduino / robot hardware connected during EEG recording
Short self-recording sessions first
```
