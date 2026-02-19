# Easun SMW 8kW - Home Assistant Integration

Local serial integration for Easun SMW 8kW inverter using the PI30 protocol over RS232.

## Features

- Local polling via USB-RS232 cable (no cloud dependency)
- Dual MPPT support (PV1 + PV2)
- Real-time sensors: AC output, battery, solar input, load, temperature
- Warning/fault status monitoring
- Working mode detection (Battery / Line / Solar)

## Requirements

- Easun SMW 8kW inverter (or compatible PI30 protocol inverter)
- USB to RS232 cable connected to HA host
- Home Assistant 2023.1.0+

## Installation via HACS

1. Add this repository to HACS as a custom repository:
   - HACS → Integrations → ⋮ → Custom repositories
   - URL: `https://github.com/TheJudge01/easun-smw8-ha`
   - Category: Integration
2. Install "Easun SMW 8kW Inverter" from HACS
3. Restart Home Assistant
4. Go to **Settings → Integrations → Add Integration → Easun SMW 8kW**
5. Enter your serial port (default: `/dev/ttyUSB0`)

## Manual Installation

Copy `custom_components/easun_smw8/` to your HA `config/custom_components/` folder and restart.

## Sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| AC Output Voltage | Output voltage | V |
| AC Output Active Power | Power consumed by loads | W |
| AC Output Apparent Power | Apparent power | VA |
| AC Output Frequency | Output frequency | Hz |
| Output Load Percent | Load percentage | % |
| Battery Voltage | Battery pack voltage | V |
| Battery Capacity | State of charge | % |
| Battery Charging Current | Charging current | A |
| Battery Discharge Current | Discharge current | A |
| PV Input Voltage | MPPT1 panel voltage | V |
| PV Input Current | MPPT1 panel current | A |
| PV Input Power | MPPT1 power | W |
| PV2 Input Voltage | MPPT2 panel voltage | V |
| PV2 Input Current | MPPT2 panel current | A |
| PV2 Input Power | MPPT2 power | W |
| Working Mode | Battery / Line / Solar | - |
| Inverter Temperature | Heat sink temp | °C |
| Has Warning | Any active warning | bool |

## Protocol

Uses PI30 serial protocol at 2400 baud, 8N1. Commands: `QPIGS`, `QPIGS2`, `QMODI`, `QPIWS`, `QPIRI`.

## Notes

- On HAOS the serial port may need permission fix: `chgrp dialout /dev/ttyUSB0`
- Tested with Prolific PL2303 USB-RS232 adapter
- Polling interval: 10 seconds

## License

MIT
