import logging
from typing import Optional, Dict, Any
from datetime import time

from .const import (
    HHCSENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder

from homeassistant.const import (
    CONF_NAME,
    STATE_UNAVAILABLE
    )
from homeassistant.components.time import (
    TimeEntity,
    TimeEntityDescription
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
        sensorTypeCompare = str(TimeEntityDescription).split(".")[-1].split("'")[0]
        if (sensorType == sensorTypeCompare):
            sensor = HHC_Time(
                conf_name,
                hub,
                device_info,
                sensor_info[0],     #slave ID
                sensor_info[1],     #modbus address
                sensor_info[2],     #sensor description
            )
            entities.append(sensor)

    async_add_entities(entities)
    return True

class HHC_Time(TimeEntity):
    """Representation of an HHC Time."""

    def __init__(self, platform_name, hub, device_info, slaveId: int, address: int, sensor: TimeEntityDescription) -> None:
        """Initialize the selector."""
        self.entity_description = sensor
        self._platform_name = platform_name
        self._hub = hub
        self._device_info = device_info
        self._slaveId = slaveId
        self._address = address
        self._data = None

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_homeheatcontrol_sensor(self)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_homeheatcontrol_sensor(self)

    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @property
    def icon(self):
        """Return the sensor icon."""
        return self.entity_description.icon

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
    def state(self) -> str | None:
        if self._data is not None and self.native_value is not None:
            return self.native_value.isoformat()
        else:
            return STATE_UNAVAILABLE
    
    @property
    def native_value(self) -> time:
        if self._data is not None:
            try:
                timedata = time(
                    hour=(self._data >> 8) & 0xFF,
                    minute=self._data & 0xFF
                )
                return timedata
            except:
                #exception if reported time in invalid so that the entity is still available and can be changed
                timedata = time(
                    hour=0,
                    minute=0
                )
                return timedata
        else:
            return None

    async def async_set_value(self, value: time) -> None:
        return
        """Change the selected value."""
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_16bit_int(int(value / self._modbus_scaling))

        _LOGGER.debug(f"try to write: Value:{value}/{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")

        response = self._hub.write_registers(unit=self._slaveId, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write: Value:{value}/{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
            return

        self._data = value / self._modbus_scaling
        self.async_write_ha_state()
