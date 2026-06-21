# OpenBCI GUI installation and connection log v0.1

## 1. Purpose

This document records the OpenBCI GUI installation, Cyton connection setup, and connection-level outcomes for Session 10.

The purpose is to document the software/hardware connection environment used for the initial OpenBCI acquisition sanity check.

Detailed signal-level and scalp-contact troubleshooting is documented separately in `docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md`.

## 2. System environment

* OS: Windows 11
* OpenBCI GUI version: v6.0.0-beta.1
* GUI build date shown: 2023/09/28
* Install source: OpenBCI Downloads page
* Execution result: success
* Administrator access warning: shown
  * Message: “This application is not being run with Administrator access. This could limit the ability to connect to devices or read/write files.”
  * Treated as failure: no
  * Reason: COM3 manual connection and live streaming succeeded

## 3. Hardware used

* OpenBCI Cyton 8-channel board
* USB dongle
* LiPo battery
* Windows 11 laptop
* OpenBCI EEG Headband Kit
* Snap cables
* Comb electrodes
* Earclip electrode pair

## 4. Safety state

* Cyton powered by LiPo battery
* Battery charging during body-connected test: no
* Arduino / robot hardware connected: no

## 5. Cyton / dongle connection settings

* USB dongle connected: yes
* Dongle switch position: GPIO6 side
* Cyton board switch position: PC
* Data source: CYTON live
* Transfer protocol: Serial from Dongle
* Manual connection: yes
* COM port: COM3
* Channel count: 8 channels

## 6. GUI connection result

* Start Session: success
* Start Data Stream: success
* Time Series widget: live traces visible
* Accelerometer values: visible
* Board-only stream test: live traces visible without body-connected electrodes

Confirmed connection path:

```text
Cyton board
→ USB dongle
→ COM3 serial connection
→ OpenBCI GUI
→ live data stream
```

## 7. Hardware Settings observed

* Ch1–Ch8 PGA Gain: x24
* Input Type: Normal
* Bias Include: Yes
* SRB2: On
* SRB1: Off

The settings were observed and recorded as the initial hardware state. Subsequent unused-channel handling during signal troubleshooting is documented separately.

## 8. Initial body-connected montage used in the first attempt

The initial body-connected montage followed the Session 09 approximate posterior montage.

- Ch1 / N1P: black snap cable, posterior-left headband position, comb electrode
- Ch2 / N2P: white snap cable, posterior-right headband position, comb electrode
- SRB / SRB2 reference function: left earclip
- BIAS: right earclip

The active electrode positions were recorded as approximate posterior-left and posterior-right headband positions, not exact 10–20 O1/O2 positions.

## 9. Scope boundary

The live stream confirmed the board-to-GUI connection path.

The board-only traces were treated as floating-input activity and environmental/electrical noise, not physiological EEG, because no body-connected electrode/reference montage was present during that check.

Detailed scalp-contact and channel troubleshooting is documented separately in `docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md`.
