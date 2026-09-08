#pragma once

#include "esphome/core/component.h"

namespace esphome::nrf52_low_power {

class NRF52LowPower : public Component {
 public:
  void setup() override;
  float get_setup_priority() const override;
};

}  // namespace esphome::nrf52_low_power
