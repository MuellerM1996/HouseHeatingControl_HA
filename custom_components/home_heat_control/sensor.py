import logging
from typing import Optional, Dict, Any
from .const import (
    HHCSENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_NAME, UnitOfEnergy, UnitOfPower
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)

from homeassistant.core import callback
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    conf_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][conf_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, conf_name)},
        "name": conf_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_info in HHCSENSOR_TYPES.values():
        if (sensor_info[0] == 0):
            sensor = HHCSensor(
                conf_name,
                hub,
                device_info,
                sensor_info[1],
                sensor_info[2],
                sensor_info[3],
                sensor_info[4],
                sensor_info[5],
            )
            entities.append(sensor)
    
    async_add_entities(entities)
    return True

class SensorBase(SensorEntity):
    """Representation of an HHC sensor."""

    def __init__(self, platform_name, hub, device_info, name, key, unit, sensorclass, icon):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._hub = hub
        self._key = key
        self._name = name
        self._unit_of_measurement = unit
        self._attr_device_class = sensorclass
        self._icon = icon
        self._device_info = device_info
        self._attr_state_class = SensorStateClass.MEASUREMENT

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_homeheatcontrol_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_homeheatcontrol_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @callback
    def _update_state(self):
        if self._key in self._hub.data:
            self._state = self._hub.data[self._key]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the sensor icon."""
        return self._icon

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info


class HHCSensor(SensorBase):
    def __init__(self, platform_name, hub, device_info, name, key, unit, sensorclass, icon):
        super().__init__(platform_name, hub, device_info, name, key, unit, sensorclass, icon)
        """Initialize the sensor."""
        
    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} ({self._name})"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        if self._key in self._hub.data:
            if (self._hub.data[self._key] == "Error"):
                return None
            return self._hub.data[self._key]