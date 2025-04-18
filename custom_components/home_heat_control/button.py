import logging
from typing import Optional, Dict, Any
from .const import (
    HHCSENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)
from homeassistant.const import (
    CONF_NAME,
)

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription
)

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
        sensorTypeCompare = str(ButtonEntityDescription).split(".")[-1].split("'")[0]
        if (sensorType == sensorTypeCompare):
            sensor = HHCButton(
                conf_name,
                hub,
                device_info,
                sensor_info[0],     #slave ID
                sensor_info[1],     #modbus address
                sensor_info[2],     #sensor description
                sensor_info[3],     #pressed value
            )
            entities.append(sensor)

    async_add_entities(entities)
    return True

class HHCButton(ButtonEntity):
    """Representation of an HHC button"""

    def __init__(self, platform_name, hub, device_info, slaveId: int, address: int, sensor: ButtonEntityDescription, pressed_value: int = 1) -> None:
        """Initialize the button."""
        self.entity_description = sensor
        self._platform_name = platform_name
        self._hub = hub
        self._device_info = device_info
        self._slaveId = slaveId
        self._address = address
        self._pressed_value = pressed_value

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._hub.async_add_homeheatcontrol_sensor(self)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_homeheatcontrol_sensor(self)

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

    async def async_press(self) -> None:
        """Press the button."""
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_16bit_uint(int(self._pressed_value))
        
        _LOGGER.debug(f"try to write: Value:{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
          
        response = self._hub.write_registers(unit=self._slaveId, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write: Value:{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
            return
