"""Optional low-power helpers for nRF52 boards."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome.components.zephyr import zephyr_add_prj_conf

DEPENDENCIES = ["nrf52"]

nrf52_low_power_ns = cg.esphome_ns.namespace("nrf52_low_power")
NRF52LowPower = nrf52_low_power_ns.class_("NRF52LowPower", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(NRF52LowPower),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    # The XIAO board definition enables its external QSPI NOR flash. Device PM
    # is required for the Zephyr driver to send the flash into deep power-down
    # and switch the QSPI pins to their sleep state.
    zephyr_add_prj_conf("PM_DEVICE", True)

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
