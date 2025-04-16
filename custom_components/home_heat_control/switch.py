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
    STATE_UNAVAILABLE
)

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription
)

from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    conf_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][conf_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, conf_name)},
        "name": conf_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_info in HHCSENSOR_TYPES:
        sensorType = str(type(sensor_info[2])).split(".")[-1].split("'")[0]
        sensorTypeCompare = str(SwitchEntityDescription).split(".")[-1].split("'")[0]
        if (sensorType == sensorTypeCompare):
            sensor = HHCSwitch(
                conf_name,
                hub,
                device_info,
                sensor_info[0],
                sensor_info[1],
                sensor_info[2],
            )
            entities.append(sensor)

    async_add_entities(entities)
    return True

class HHCSwitch(SwitchEntity):
    """Representation of an HHC switch"""

    def __init__(self, platform_name, hub, device_info, slaveId: int, address: int, sensor: SwitchEntityDescription) -> None:
        """Initialize the switch."""
        self.entity_description = sensor
        self._platform_name = platform_name
        self._hub = hub
        self._device_info = device_info
        self._slaveId = slaveId
        self._address = address
        self._data = None
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._hub.async_add_homeheatcontrol_sensor(self)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_homeheatcontrol_sensor(self)

    def _modbus_data_updated(self) -> None:
        self.async_write_ha_state()

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
        if self._data is not None:
            self._attr_is_on = self._data
        else:
            return STATE_UNAVAILABLE
        if self._attr_is_on:
            return STATE_ON
        else:
            return STATE_OFF    
    
    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        """Change the selected value."""
        value = 1
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_16bit_uint(int(value))
        
        _LOGGER.debug(f"try to write: Value:{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
          
        response = self._hub.write_registers(unit=self._slaveId, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write: Value:{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
            return
        
        self._data = True
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        """Change the selected value."""
        value = 0
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_16bit_uint(int(value))
        
        _LOGGER.debug(f"try to write: Value:{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
            
        response = self._hub.write_registers(unit=self._slaveId, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write: Value:{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
            return
        
        self._data = False
        self.async_write_ha_state()
