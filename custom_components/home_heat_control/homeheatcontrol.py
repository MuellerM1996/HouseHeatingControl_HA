import logging
import threading
from typing import Optional
from datetime import timedelta

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)

def bitfield(value, size=None):
    """convert a int to a bitfield represented in a list"""    
    if size is not None:
            return [int(digit) for digit in bin(value)[2:].zfill(size)] # [2:] to chop off the "0b" part 
    else:
            return [int(digit) for digit in bin(value)[2:]]             # [2:] to chop off the "0b" part 

class HomeHeatControl:
    """Thread safe wrapper class for pymodbus."""

    def __init__(self, hass, name, host, port, address, scan_interval):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(host=host, port=port, timeout=max(3, (scan_interval - 1)))
        self._lock = threading.Lock()
        self._name = name
        self._address = address
        self._scan_interval = timedelta(seconds=scan_interval)
        self._unsub_interval_method = None
        self._sensors = []
        self.data = {}
            
    @callback
    def async_add_homeheatcontrol_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
           # self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_homeheatcontrol_sensor(self, update_callback):
        """Remove data update."""
        self._sensors.remove(update_callback)

        if not self._sensors:
            """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()

    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> dict:
        """Time to update."""
        result : bool = await self._hass.async_add_executor_job(self._refresh_modbus_data)
        if result:
            for update_callback in self._sensors:
                update_callback()


    def _refresh_modbus_data(self, _now: Optional[int] = None) -> bool:
        """Time to update."""
        if not self._sensors:
            return False

        if not self._check_and_reconnect():
            #if not connected, skip
            return False

        try:
            update_result = self.read_modbus_data()
        except Exception as e:
            _LOGGER.exception("Error reading modbus data", exc_info=True)
            update_result = False
        return update_result

    @property
    def name(self):
        """Return the name of this hub."""
        return self._name

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def _check_and_reconnect(self):
        if not self._client.connected:
            _LOGGER.info("modbus client is not connected, trying to reconnect")
            return self.connect()
        return self._client.connected

    def connect(self):
        """Connect client."""
        result = False
        with self._lock:
            result = self._client.connect()

        if result:
            _LOGGER.info("successfully connected to %s:%s",
                         self._client.comm_params.host, self._client.comm_params.port)
        else:
            _LOGGER.warning("not able to connect to %s:%s",
                            self._client.comm_params.host, self._client.comm_params.port)
        return result
    

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        with self._lock:
            return self._client.read_holding_registers(
                address=address, count=count, slave=unit
            )

    def write_registers(self, unit, address, payload):
        """Write registers."""
        with self._lock:
            return self._client.write_registers(
                address=address, values=payload, slave=unit
            )
            
    def write_register(self, unit, address, payload):
        """Write register."""
        with self._lock:
            return self._client.write_register(
                address=address, value=payload, slave=unit
            )
            
    def read_modbus_data(self):
        return (
            self.read_modbus_data_sw_Version(),
            self.read_modbus_data_dtc_active(),
            self.read_modbus_data_outsidetemperature(),
            self.read_modbus_data_room1temperature(),
            self.read_modbus_data_room2temperature(),
            self.read_modbus_data_doorbellstatus(),
            self.read_modbus_data_heatcontrolmanagement_active()
        )

    def read_modbus_data_sw_Version(self, start_address=0):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=3)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)
        
        fbl_sw_version_major = decoder.decode_8bit_uint()
        fbl_sw_version_minor = decoder.decode_8bit_uint()
        fbl_sw_version_patch = decoder.decode_8bit_uint()
        appl_sw_version_major = decoder.decode_8bit_uint()
        appl_sw_version_minor = decoder.decode_8bit_uint()
        appl_sw_version_patch = decoder.decode_8bit_uint()

        self.data["fbl_sw_version"] = f"{fbl_sw_version_major}.{fbl_sw_version_minor}.{fbl_sw_version_patch}"
        self.data["appl_sw_version"] = f"{appl_sw_version_major}.{appl_sw_version_minor}.{appl_sw_version_patch}"
        
        return True
    
    def read_modbus_data_dtc_active(self, start_address=3):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["dtcactive"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_outsidetemperature(self, start_address=20):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if (temperature_raw == 0x7FFD):
            self.data["outsidetemperature"] = "Nicht verbaut"
        elif (temperature_raw == 0x7FFE):
            self.data["outsidetemperature"] = "Init"
        elif (temperature_raw == 0x7FFF):
            self.data["outsidetemperature"] = "Fehler"
        else:
            self.data["outsidetemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_room1temperature(self, start_address=21):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if (temperature_raw == 0x7FFD):
            self.data["room1temperature"] = "Nicht verbaut"
        elif (temperature_raw == 0x7FFE):
            self.data["room1temperature"] = "Init"
        elif (temperature_raw == 0x7FFF):
            self.data["room1temperature"] = "Fehler"
        else:
            self.data["room1temperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_room2temperature(self, start_address=22):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if (temperature_raw == 0x7FFD):
            self.data["room2temperature"] = "Nicht verbaut"
        elif (temperature_raw == 0x7FFE):
            self.data["room2temperature"] = "Init"
        elif (temperature_raw == 0x7FFF):
            self.data["room2temperature"] = "Fehler"
        else:
            self.data["room2temperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_doorbellstatus(self, start_address=25):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        doorbellstatus = decoder.decode_16bit_uint()

        if (doorbellstatus == 0):
            self.data["doorbell_status"] = "Nicht verbaut"
        elif (doorbellstatus == 1):
            self.data["doorbell_status"] = "AUS"
        elif (doorbellstatus == 2):
            self.data["doorbell_status"] = "AN"
        elif (doorbellstatus == 3):
            self.data["doorbell_status"] = "Fehler"
        else:
            self.data["doorbell_status"] = None
        
        return True
    
    def read_modbus_data_heatcontrolmanagement_active(self, start_address=30):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["heatcontrolmanagement_enabled"] = decoder.decode_16bit_uint() != 0
        
        return True
