import logging
from typing import Optional, Dict, Any

from .const import (
    HHCSENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder

from homeassistant.const import (
    CONF_NAME,
    STATE_OK,
    STATE_UNAVAILABLE
    )
from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription
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
        sensorTypeCompare = str(SelectEntityDescription).split(".")[-1].split("'")[0]
        if (sensorType == sensorTypeCompare):
            sensor = HHCSelect(
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

class HHCSelect(SelectEntity):
    """Representation of an HHC number."""

    def __init__(self, platform_name, hub, device_info, slaveId: int, address: int, sensor: SelectEntityDescription) -> None:
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
        if self._data is not None:
            return self.current_option
        else:
            return STATE_UNAVAILABLE
    
    @property
    def current_option(self) -> str | None:
        if self._data == 1:
            return self.options[1]
        elif self._data == 2:
            return self.options[2]
        else:
            return self.options[0]

    async def async_select_option(self, option: str) -> None:
        """Change the selected value."""
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        temp = -1
        try:
            temp = self.options.index(option)
        except:
            _LOGGER.error(f"Could not write: Option:{option}, Name:{self.entity_description.key}, Address:{self._address} - Option not in list")
            return
        builder.add_16bit_uint(temp)

        _LOGGER.debug(f"try to write: Value:{option}/{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")

        response = self._hub.write_registers(unit=self._slaveId, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write: Value:{option}/{builder.to_registers()}, Name:{self.entity_description.key}, Address:{self._address}")
            return

        self._data = temp
        self.async_write_ha_state()
