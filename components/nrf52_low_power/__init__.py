"""Optional low-power helpers for nRF52 boards."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome.components.zephyr import zephyr_add_prj_conf
from esphome.components.zephyr import zephyr_add_overlay

DEPENDENCIES = ["nrf52"]

nrf52_low_power_ns = cg.esphome_ns.namespace("nrf52_low_power")
NRF52LowPower = nrf52_low_power_ns.class_("NRF52LowPower", cg.Component)

CONF_DISABLE_USB_UART = "disable_usb_uart"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(NRF52LowPower),
        cv.Optional(CONF_DISABLE_USB_UART, default=False): cv.boolean,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    # The XIAO board definition enables its external QSPI NOR flash. Device PM
    # is required for the Zephyr driver to send the flash into deep power-down
    # and switch the QSPI pins to their sleep state.
    zephyr_add_prj_conf("PM_DEVICE", True)

    if config[CONF_DISABLE_USB_UART]:
        # The XIAO board defaults enable the application USB device and UART0.
        # Neither is needed for UF2 flashing, which runs in the separate
        # Adafruit bootloader entered with a double reset.
        zephyr_add_prj_conf("SERIAL", False)
        zephyr_add_prj_conf("USB_DEVICE_STACK", False)
        zephyr_add_prj_conf("USB_CDC_ACM", False)
        zephyr_add_overlay(
            """
                &zephyr_udc0 {
                    status = "disabled";
                };

                &uart0 {
                    status = "disabled";
                };
            """
        )

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
