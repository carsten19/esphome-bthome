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
      ref: v0.1.0-nrf52
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
nrf52:
  board: xiao_ble
  dcdc: true

bthome:
  min_interval: 5s
  max_interval: 10s
  tx_power: -4
```

The values above are a conservative starting point. Verify radio coverage and
measure the complete board; the component fix removes unnecessary application
polling but does not eliminate board-level regulator, flash, sensor, or divider
current.

## License

MIT License - See [bthome.io](https://bthome.io/) for protocol specification.
