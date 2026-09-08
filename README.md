# ESPHome BTHome Component

A custom ESPHome component that broadcasts sensor data using the [BTHome v2](https://bthome.io/) BLE protocol for seamless Home Assistant integration.

## Features

- **BTHome v2 Protocol** - Full compliance with the BTHome specification
- **Multi-Platform** - ESP32 (ESP-IDF) and nRF52 (Zephyr)
- **60+ Sensor Types** - Temperature, humidity, pressure, power, and more
- **28 Binary Sensor Types** - Motion, door, window, smoke, etc.
- **AES-CCM Encryption** - Optional 128-bit encryption
- **Home Assistant Auto-Discovery** - Devices appear automatically
- **Low-Power nRF52 Loop Handling** - Lets Zephyr idle while the BLE controller handles regular advertising
- **XIAO nRF52840 Low-Power Helper** - Suspends unused QSPI flash and can disable application USB/UART

Current tested release: **[`v0.3.0-nrf52`](https://github.com/carsten19/esphome-bthome/releases/tag/v0.3.0-nrf52)**

## About This Fork

This fork combines the current upstream improvements with the nRF52 fixes that
were previously available only on a separate development branch. It also stops
polling `BTHome::loop()` when no advertisement update or retransmission is
pending. Regular BLE advertising continues in the controller, while ESPHome and
Zephyr are free to enter their idle path between events.

The fork is based on the original
[`dz0ny/esphome-bthome`](https://github.com/dz0ny/esphome-bthome) project and the
nRF52 work in [`jnimmo/esphome-bthome`](https://github.com/jnimmo/esphome-bthome).

## Quick Start

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/carsten19/esphome-bthome
      ref: v0.3.0-nrf52
    components: [bthome]

sensor:
  - platform: bme280_i2c
    temperature:
      id: temperature
    humidity:
      id: humidity

bthome:
  sensors:
    - type: temperature
      id: temperature
    - type: humidity
      id: humidity
```

Use the tagged ref for reproducible builds. `main` tracks ongoing development.

## Documentation

Full documentation is available at **[dz0ny.github.io/esphome-bthome](https://dz0ny.github.io/esphome-bthome/)**

- [Getting Started](https://dz0ny.github.io/esphome-bthome/getting-started/introduction/)
- [Configuration](https://dz0ny.github.io/esphome-bthome/configuration/basic-setup/)
- [Device Examples](https://dz0ny.github.io/esphome-bthome/devices/1-gang-pushbutton/)
- [Sensor Reference](https://dz0ny.github.io/esphome-bthome/reference/sensor-types/)

## Supported Platforms

| Platform | Board Example | Framework |
|----------|---------------|-----------|
| ESP32 | esp32dev, XIAO ESP32-C3 | ESP-IDF |
| nRF52840 | Seeed XIAO BLE | Zephyr |

### nRF52 Low-Power Configuration

On nRF52, omit the `logger:` block for low-power deployments. An empty logger
configuration selects and initializes the USB CDC logging path.

```yaml
esphome:
  name: bthome-lux-nrf52
  on_boot:
    - priority: -100
      then:
        # The default ESPHome loop interval is 16 ms. One second is sufficient
        # for this slow sensor; BLE advertising continues in the controller.
        - lambda: |-
            App.set_loop_interval(1000);

nrf52:
  board: xiao_ble
  dcdc: true

external_components:
  - source:
      type: git
      url: https://github.com/carsten19/esphome-bthome
      ref: v0.3.0-nrf52
    components: [bthome, nrf52_low_power]

# XIAO nRF52840 only: suspend the unused external QSPI flash and disable
# application USB/UART. UF2 flashing through the bootloader remains available.
nrf52_low_power:
  disable_usb_uart: true

bthome:
  trigger_based: false
  min_interval: 5s
  max_interval: 10s
  tx_power: -4
```

The XIAO nRF52840 board definition initializes the onboard external QSPI flash.
When the application does not use that flash, `nrf52_low_power` enables Zephyr
device power management and suspends the flash after boot. This sends the flash
into deep power-down and switches the QSPI pins to their sleep state. Do not use
the helper if your application stores data on the external QSPI flash.

With `disable_usb_uart: true`, the application USB device and UART0 are disabled
as well. This removes a large idle-current penalty from the default XIAO Zephyr
board configuration.

Still available:

- USB power and hardware battery charging through the onboard BQ25101
- UF2 flashing through the separate Adafruit bootloader: double-press reset and
  copy the UF2 file to the mounted bootloader drive

Unavailable while this option is enabled:

- Runtime USB CDC logging and serial console
- The 1200-baud software trigger for entering the bootloader
- UART0 for external serial devices

Do not add a `logger:` block or a UART component with this option.

On a real XIAO nRF52840 with BTHome advertising every 5–10 seconds, an OPT3001
and battery sensing, a µA meter displayed about 10 µA at idle, about 15 µA during
visible advertising activity and briefly more than 80 µA during an illuminance
measurement. Actual radio peaks are much higher and much shorter than a regular
multimeter can resolve; use a fast power analyzer for accurate energy figures.

The one-second application loop interval is appropriate for slow environmental
sensors. Reduce or remove it for buttons, pulse counters or other components
that require sub-second response times.

The values above are a conservative starting point. Verify radio coverage and
measure the complete board; the component fix removes unnecessary application
polling but does not eliminate board-level regulator, flash, sensor, or divider
current.

## License

MIT License - See [bthome.io](https://bthome.io/) for protocol specification.
