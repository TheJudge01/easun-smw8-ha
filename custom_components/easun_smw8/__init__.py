"""Easun SMW 8kW Inverter integration - PI30 Serial Protocol."""
from __future__ import annotations

import logging
import serial
import time
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "easun_smw8"
PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SCAN_INTERVAL = timedelta(seconds=10)

COMMANDS = {
    "QPIGS":  bytes([0x51, 0x50, 0x49, 0x47, 0x53, 0xb7, 0xa9, 0x0d]),
    "QPIGS2": bytes([0x51, 0x50, 0x49, 0x47, 0x53, 0x32, 0x68, 0x2d, 0x0d]),
    "QPIWS":  bytes([0x51, 0x50, 0x49, 0x57, 0x53, 0xb4, 0xda, 0x0d]),
    "QMODI":  bytes([0x51, 0x4d, 0x4f, 0x44, 0x49, 0xc1, 0x0d]),
    "QPIRI":  bytes([0x51, 0x50, 0x49, 0x52, 0x49, 0xf8, 0x54, 0x0d]),
}


def send_command(port: str, cmd_bytes: bytes, timeout: int = 3) -> str:
    try:
        with serial.Serial(port=port, baudrate=2400, bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                           timeout=timeout, xonxoff=False, rtscts=False, dsrdtr=False) as ser:
            ser.reset_input_buffer()
            ser.write(cmd_bytes)
            time.sleep(0.5)
            response = ser.read(256)
            if response:
                return response.decode("ascii", errors="replace").strip()
    except Exception as ex:
        _LOGGER.error("Serial error on %s: %s", port, ex)
    return ""


def parse_qpigs(response: str) -> dict:
    if not response.startswith("("):
        return {}
    parts = response[1:].split()
    if len(parts) < 20:
        return {}
    try:
        return {
            "grid_voltage":                   float(parts[0]),
            "grid_frequency":                 float(parts[1]),
            "ac_output_voltage":              float(parts[2]),
            "ac_output_frequency":            float(parts[3]),
            "ac_output_apparent_power":       int(parts[4]),
            "ac_output_active_power":         int(parts[5]),
            "output_load_percent":            int(parts[6]),
            "bus_voltage":                    int(parts[7]),
            "battery_voltage":                float(parts[8]),
            "battery_charging_current":       int(parts[9]),
            "battery_capacity":               int(parts[10]),
            "inverter_heat_sink_temperature": int(parts[11]),
            "pv_input_current":               float(parts[12]),
            "pv_input_voltage":               float(parts[13]),
            "battery_voltage_from_scc":       float(parts[14]),
            "battery_discharge_current":      int(parts[15]),
            "device_status":                  parts[16],
            "pv_input_power":                 int(parts[19]) if len(parts) > 19 else 0,
        }
    except (ValueError, IndexError) as ex:
        _LOGGER.warning("Failed to parse QPIGS: %s", ex)
        return {}


def parse_qpigs2(response: str) -> dict:
    if not response.startswith("("):
        return {}
    parts = response[1:].split()
    if len(parts) < 3:
        return {}
    try:
        return {
            "pv2_input_voltage": float(parts[0]),
            "pv2_input_current": float(parts[1]),
            "pv2_input_power":   int(parts[2]),
        }
    except (ValueError, IndexError):
        return {}


def parse_qmodi(response: str) -> dict:
    if not response.startswith("("):
        return {}
    mode_char = response[1:2]
    modes = {"P": "Power On", "S": "Standby", "L": "Line",
             "B": "Battery", "F": "Fault", "H": "Power Saving"}
    return {"working_mode": modes.get(mode_char, f"Unknown ({mode_char})")}


def parse_qpiws(response: str) -> dict:
    if not response.startswith("("):
        return {}
    clean = "".join(c for c in response[1:].strip() if c in "01")
    warning_map = {
        0: "inverter_fault", 1: "bus_over", 2: "bus_under", 3: "bus_soft_fail",
        4: "line_fail", 5: "opv_short", 6: "inverter_voltage_too_low",
        7: "inverter_voltage_too_high", 8: "over_temperature", 9: "fan_locked",
        10: "battery_voltage_high", 11: "battery_low_alarm", 13: "battery_under_shutdown",
        15: "overload", 16: "eeprom_fault", 17: "inverter_over_current",
        18: "inverter_soft_fail", 19: "self_test_fail", 20: "op_dc_voltage_over",
        21: "bat_open", 22: "current_sensor_fail", 23: "battery_short",
        24: "power_limit", 25: "pv_voltage_high", 26: "mppt_overload_fault",
        27: "mppt_overload_warning", 28: "battery_too_low_to_charge",
    }
    result = {"has_warning": False}
    for i, bit in enumerate(clean):
        if i in warning_map:
            active = bit == "1"
            result[warning_map[i]] = active
            if active:
                result["has_warning"] = True
    return result


def parse_qpiri(response: str) -> dict:
    if not response.startswith("("):
        return {}
    parts = response[1:].split()
    if len(parts) < 15:
        return {}
    try:
        return {
            "rated_battery_voltage":    float(parts[7]),
            "battery_recharge_voltage": float(parts[8]),
            "battery_under_voltage":    float(parts[9]),
            "battery_bulk_voltage":     float(parts[10]),
            "battery_float_voltage":    float(parts[11]),
            "max_ac_charging_current":  int(parts[13]),
            "max_charging_current":     int(parts[14]),
        }
    except (ValueError, IndexError):
        return {}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    port = entry.data["port"]

    async def async_update_data():
        def fetch():
            result = {}
            result.update(parse_qpigs(send_command(port, COMMANDS["QPIGS"])))

            r2 = send_command(port, COMMANDS["QPIGS2"])
            if r2.startswith("(") and not r2.startswith("(NAK"):
                result.update(parse_qpigs2(r2))
            else:
                result.update({"pv2_input_voltage": 0.0, "pv2_input_current": 0.0, "pv2_input_power": 0})

            result.update(parse_qmodi(send_command(port, COMMANDS["QMODI"])))
            result.update(parse_qpiws(send_command(port, COMMANDS["QPIWS"])))
            result.update(parse_qpiri(send_command(port, COMMANDS["QPIRI"])))
            return result

        try:
            data = await hass.async_add_executor_job(fetch)
        except Exception as ex:
            raise UpdateFailed(f"Error communicating with inverter: {ex}") from ex

        if not data:
            raise UpdateFailed("Empty response from inverter")
        return data

    coordinator = DataUpdateCoordinator(
        hass, _LOGGER, name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
