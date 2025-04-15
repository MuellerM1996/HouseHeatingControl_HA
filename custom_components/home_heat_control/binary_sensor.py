import logging
from typing import Optional, Dict, Any
from .const import (
    HHCSENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)
from homeassistant.const import (
    CONF_NAME,
    STATE_ON,
    STATE_OFF,
    STATE_UNKNOWN
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription
)

from homeassistant.core import callback

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
    for sensor_info in HHCSENSOR_TYPES:
        sensorType = str(type(sensor_info[0])).split(".")[-1].split("'")[0]
        sensorTypeCompare = str(BinarySensorEntityDescription).split(".")[-1].split("'")[0]
        if (sensorType == sensorTypeCompare):
            sensor = HHCBinarySensor(
                conf_name,
                hub,
                device_info,
                sensor_info[0],
            )
            entities.append(sensor)

    async_add_entities(entities)
    return True

class HHCBinarySensor(BinarySensorEntity):
    """Representation of an binary HHC sensor."""

    def __init__(self, platform_name, hub, device_info, sensor: BinarySensorEntityDescription):
        """Initialize the sensor."""
        self.entity_description = sensor
        self._platform_name = platform_name
        self._hub = hub
        self._device_info = device_info

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
        if self.entity_description.key in self._hub.data:
            self._state = self._hub.data[self.entity_description.key]

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"
        
    @property
    def state(self):
        """Return the state of the sensor."""
        if self.entity_description.key in self._hub.data:
            self._attr_is_on = self._hub.data[self.entity_description.key]
            if self._attr_is_on:
                return STATE_ON
            else:
                return STATE_OFF
        else:
            return STATE_UNKNOWN