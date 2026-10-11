# ESPHome Component Implementation Plan for EG9 Climate

This document outlines the functional requirements and architecture of the custom `eg9_climate` component for ESPHome.

## 1. User Interface and Functionality in Home Assistant

The component provides a standard climate control interface in Home Assistant with the following capabilities:

### 1.1. Operating Modes (`hvac_mode`)

Supported modes:
- **`Cool`:** Air conditioning cooling mode.
- **`Heat`:** Air conditioning heating mode.
- **`Off`:** Turns off the AC unit using a dedicated, pre-recorded static "OFF" command frame.

### 1.2. Target Temperature (`target_temperature`)

- Full target temperature selection support.
- Temperature range: **16°C to 31°C**.
- Step size: 1.0°C.

### 1.3. Fan Speeds (`fan_mode`)

Supported speeds:
- `Auto`
- `Low`
- `Medium`
- `High`
- `Quiet` (Silent/Sleep mode)

### 1.4. Vertical Vane Position (`swing_mode` & Custom Presets)

Supported positions/presets:
- `Auto` (Automatic vane position)
- `Top` (Highest position)
- `Medium-Top`
- `Medium` (Center position)
- `Medium-Bottom`
- `Bottom` (Lowest position)
- `Swing` (Continuous oscillation mode, activates `CLIMATE_SWING_VERTICAL`)

## 2. IR Command Generation Architecture

The implementation uses a hybrid approach: dynamic frame payload construction combined with a pre-recorded lookup dictionary for checksums.

### 2.1. Dataset
- Exhaustive IR captures covering both **Cool** and **Heat** modes across all 16 temperatures, 5 fan speeds, and 7 vane positions (560 combinations per mode, stored in `tools/dumps/ir_dictionary.csv`).

### 2.2. Lookup Dictionary
- An embedded C++ dictionary `std::map<std::vector<uint8_t>, std::pair<uint8_t, uint8_t>> EG9Climate::IR_CODE_DICTIONARY`.
- **Key:** A 7-byte `std::vector<uint8_t>` (`B6`...`B12`) representing the unique state settings (Power, Mode, Encoded Temperature, Fan/Swing byte, and reserved bytes).
- **Value:** `std::pair<uint8_t, uint8_t>` containing the matching `B13` and `B14` (CRC) bytes.

### 2.3. Runtime Transmission Workflow
1. **Power Off Mode:** Sends the static 14-byte OFF frame.
2. **Active Mode (`Cool` / `Heat`):**
   - The component constructs the 7-byte settings key on the fly based on user input.
   - It performs a lookup in `IR_CODE_DICTIONARY`.
   - **If key is found:** Prepend header bytes `B1`...`B5`, append the retrieved `B13` and `B14` bytes, and transmit the 14-byte frame via `RemoteTransmitter`.
   - **If key is not found:** Attempts a fallback vane mode; if that also fails, logs a warning/error and halts transmission.
