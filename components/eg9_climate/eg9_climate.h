#pragma once

#include "esphome/components/climate/climate.h"
#include "esphome/components/remote_transmitter/remote_transmitter.h"
#include "esphome/components/select/select.h"
#include <vector>
#include <map>
#include <utility>

namespace esphome {
namespace eg9_climate {

// Protocol constants
const uint8_t EG9_HEADER[] = {0xC4, 0xD3, 0x64, 0x80, 0x00};
const uint8_t EG9_POWER_ON = 0x24;
const uint8_t EG9_MODE_COOL = 0xC0;
const uint8_t EG9_MODE_HEAT = 0x80;

// Temperature is encoded as (31 - temp)
const uint8_t EG9_TEMP_OFFSET = 31;

// Mappings for B9 byte construction
// B9 = (FanCode << 5) | SwingCode

// 3-bit codes for Fan Speed
enum Eg9FanCode : uint8_t {
    FAN_CODE_AUTO = 0b000,
    FAN_CODE_QUIET = 0b100,
    FAN_CODE_LOW = 0b010,
    FAN_CODE_MEDIUM = 0b110,
    FAN_CODE_HIGH = 0b101,
};

// 5-bit codes for Vane Position
enum Eg9SwingCode : uint8_t {
    SWING_CODE_AUTO           = 0b00000, // 0
    SWING_CODE_TOP            = 0b10000, // 16
    SWING_CODE_MEDIUM_TOP     = 0b01000, // 8
    SWING_CODE_MEDIUM         = 0b11000, // 24
    SWING_CODE_MEDIUM_BOTTOM  = 0b00100, // 4
    SWING_CODE_BOTTOM         = 0b10100, // 20
    SWING_CODE_CONTINUOUS     = 0b11100, // 28
};

class EG9Climate;

class EG9VaneSelect : public select::Select {
 public:
  void set_parent(EG9Climate *parent) { this->parent_ = parent; }

 protected:
  void control(const std::string &value) override;

  EG9Climate *parent_{nullptr};
};

class EG9Climate : public climate::Climate, public Component {
 public:
  EG9Climate();
  void set_transmitter(remote_transmitter::RemoteTransmitterComponent *transmitter) {
    this->transmitter_ = transmitter;
  }
  void set_vane_select(EG9VaneSelect *vane_select) {
    this->vane_select_ = vane_select;
  }

  void setup() override;
  climate::ClimateTraits traits() override;
  void set_vane_position(const std::string &position);
  void set_has_vane_select(bool has_vane_select) { this->has_vane_select_ = has_vane_select; }

 protected:
  void control(const climate::ClimateCall &call) override;
  void transmit_state();
  
  uint8_t reverse_bits(uint8_t data) const;

  remote_transmitter::RemoteTransmitterComponent *transmitter_;
  EG9VaneSelect *vane_select_{nullptr};
  bool has_vane_select_{false};
  Eg9SwingCode current_swing_code_{SWING_CODE_AUTO};

  static const std::map<std::vector<uint8_t>, std::pair<uint8_t, uint8_t>> IR_CODE_DICTIONARY;
};

}  // namespace eg9_climate
}  // namespace esphome
