#include "nrf52_low_power.h"

#include "esphome/core/log.h"

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/pm/device.h>

namespace esphome::nrf52_low_power {

static const char *const TAG = "nrf52_low_power";

void NRF52LowPower::setup() {
#if DT_NODE_EXISTS(DT_NODELABEL(p25q16h)) && DT_NODE_HAS_STATUS(DT_NODELABEL(p25q16h), okay)
  const struct device *flash = DEVICE_DT_GET(DT_NODELABEL(p25q16h));
  if (!device_is_ready(flash)) {
    ESP_LOGW(TAG, "External QSPI flash is not ready; cannot suspend it");
    this->mark_failed();
    return;
  }

  const int result = pm_device_action_run(flash, PM_DEVICE_ACTION_SUSPEND);
  if (result < 0) {
    ESP_LOGW(TAG, "Failed to suspend external QSPI flash: %d", result);
    this->mark_failed();
    return;
  }

  ESP_LOGI(TAG, "External QSPI flash suspended");
#else
  ESP_LOGW(TAG, "No supported external QSPI flash found");
  this->mark_failed();
#endif
}

float NRF52LowPower::get_setup_priority() const { return setup_priority::HARDWARE; }

}  // namespace esphome::nrf52_low_power
