"""Sensor platform for Easun SMW 8kW integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN

# (key, name, unit, device_class, state_class, icon)
SENSOR_DEFINITIONS = [
    ("ac_output_voltage",               "AC Output Voltage",            UnitOfElectricPotential.VOLT,   SensorDeviceClass.VOLTAGE,      SensorStateClass.MEASUREMENT, None),
    ("ac_output_frequency",             "AC Output Frequency",          UnitOfFrequency.HERTZ,          SensorDeviceClass.FREQUENCY,    SensorStateClass.MEASUREMENT, None),
    ("ac_output_apparent_power",        "AC Output Apparent Power",     "VA",                           SensorDeviceClass.APPARENT_POWER, SensorStateClass.MEASUREMENT, None),
    ("ac_output_active_power",          "AC Output Active Power",       UnitOfPower.WATT,               SensorDeviceClass.POWER,        SensorStateClass.MEASUREMENT, None),
    ("output_load_percent",             "Load Percent",                 PERCENTAGE,                     None,                           SensorStateClass.MEASUREMENT, "mdi:gauge"),
    ("grid_voltage",                    "Grid Voltage",                 UnitOfElectricPotential.VOLT,   SensorDeviceClass.VOLTAGE,      SensorStateClass.MEASUREMENT, None),
    ("grid_frequency",                  "Grid Frequency",               UnitOfFrequency.HERTZ,          SensorDeviceClass.FREQUENCY,    SensorStateClass.MEASUREMENT, None),
    ("bus_voltage",                     "Bus Voltage",                  UnitOfElectricPotential.VOLT,   SensorDeviceClass.VOLTAGE,      SensorStateClass.MEASUREMENT, None),
    ("battery_voltage",                 "Battery Voltage",              UnitOfElectricPotential.VOLT,   SensorDeviceClass.VOLTAGE,      SensorStateClass.MEASUREMENT, None),
    ("battery_charging_current",        "Battery Charging Current",     UnitOfElectricCurrent.AMPERE,   SensorDeviceClass.CURRENT,      SensorStateClass.MEASUREMENT, None),
    ("battery_discharge_current",       "Battery Discharge Current",    UnitOfElectricCurrent.AMPERE,   SensorDeviceClass.CURRENT,      SensorStateClass.MEASUREMENT, None),
    ("battery_capacity",                "Battery Capacity",             PERCENTAGE,                     SensorDeviceClass.BATTERY,      SensorStateClass.MEASUREMENT, None),
    ("inverter_heat_sink_temperature",  "Inverter Temperature",         UnitOfTemperature.CELSIUS,      SensorDeviceClass.TEMPERATURE,  SensorStateClass.MEASUREMENT, None),
    ("pv_input_voltage",                "PV Input Voltage",             UnitOfElectricPotential.VOLT,   SensorDeviceClass.VOLTAGE,      SensorStateClass.MEASUREMENT, None),
    ("pv_input_current",                "PV Input Current",             UnitOfElectricCurrent.AMPERE,   SensorDeviceClass.CURRENT,      SensorStateClass.MEASUREMENT, None),
    ("pv_input_power",                  "PV Input Power",               UnitOfPower.WATT,               SensorDeviceClass.POWER,        SensorStateClass.MEASUREMENT, None),
    ("pv2_input_voltage",               "PV2 Input Voltage",            UnitOfElectricPotential.VOLT,   SensorDeviceClass.VOLTAGE,      SensorStateClass.MEASUREMENT, None),
    ("pv2_input_current",               "PV2 Input Current",            UnitOfElectricCurrent.AMPERE,   SensorDeviceClass.CURRENT,      SensorStateClass.MEASUREMENT, None),
    ("pv2_input_power",                 "PV2 Input Power",              UnitOfPower.WATT,               SensorDeviceClass.POWER,        SensorStateClass.MEASUREMENT, None),
    ("working_mode",                    "Working Mode",                 None,                           None,                           None,                         "mdi:solar-power"),
    ("has_warning",                     "Has Warning",                  None,                           None,                           None,                         "mdi:alert-circle"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for sensor_def in SENSOR_DEFINITIONS:
        entities.append(EasunSensor(coordinator, entry, sensor_def))

    async_add_entities(entities)


class EasunSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Easun SMW8 sensor."""

    def __init__(self, coordinator, entry: ConfigEntry, sensor_def: tuple):
        super().__init__(coordinator)
        (
            self._key,
            self._attr_name,
            self._attr_native_unit_of_measurement,
            self._attr_device_class,
            self._attr_state_class,
            self._icon,
        ) = sensor_def

        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._entry = entry

    @property
    def icon(self):
        return self._icon

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Easun SMW 8kW",
            manufacturer="Easun Power",
            model="SMW 8kW",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data is not None
