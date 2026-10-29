"""Optional low-power helpers for nRF52 boards."""

import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.final_validate as fv
from esphome.const import CONF_BAUD_RATE, CONF_ID
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


def _final_validate(config):
    if not config[CONF_DISABLE_USB_UART]:
        return config
    full_config = fv.full_config.get()
    # Both need the application USB CDC that disable_usb_uart switches off;
    # without this check the build fails late with a Kconfig conflict.
    if "dfu" in full_config.get("nrf52", {}):
        raise cv.Invalid(
            f"'{CONF_DISABLE_USB_UART}: true' cannot be combined with 'nrf52: dfu'. "
            "Remove 'dfu' and enter the bootloader with a double reset instead.",
            path=[CONF_DISABLE_USB_UART],
        )
    logger_config = full_config.get("logger")
    if logger_config is not None and logger_config.get(CONF_BAUD_RATE) != 0:
        raise cv.Invalid(
            f"'{CONF_DISABLE_USB_UART}: true' disables the logger's serial output. "
            "Remove 'logger' or set 'baud_rate: 0'.",
            path=[CONF_DISABLE_USB_UART],
        )
    return config


FINAL_VALIDATE_SCHEMA = _final_validate


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
