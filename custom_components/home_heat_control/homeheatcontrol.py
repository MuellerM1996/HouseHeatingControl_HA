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
            self.read_modbus_data_heatcontrolmanagement_enabled(),
            self.read_modbus_data_heatcontrolmanagement_belowmintemperature(),
            self.read_modbus_data_hc1_status(),
            self.read_modbus_data_hc1_pumpstatus(),
            self.read_modbus_data_hc1_mixerstatus(),
            self.read_modbus_data_hc1_mixernormed(),
            self.read_modbus_data_hc1_mixerposition(),
            self.read_modbus_data_hc1_targetforeruntemperature(),
            self.read_modbus_data_hc1_foreruntemperature(),
            self.read_modbus_data_hc1_returnflowtemperature(),
            self.read_modbus_data_hc2_status(),
            self.read_modbus_data_hc2_pumpstatus(),
            self.read_modbus_data_hc2_mixerstatus(),
            self.read_modbus_data_hc2_mixernormed(),
            self.read_modbus_data_hc2_mixerposition(),
            self.read_modbus_data_hc2_targetforeruntemperature(),
            self.read_modbus_data_hc2_foreruntemperature(),
            self.read_modbus_data_hc2_returnflowtemperature(),
            self.read_modbus_data_hc3_status(),
            self.read_modbus_data_hc3_pumpstatus(),
            self.read_modbus_data_hc3_mixerstatus(),
            self.read_modbus_data_hc3_mixernormed(),
            self.read_modbus_data_hc3_mixerposition(),
            self.read_modbus_data_hc3_targetforeruntemperature(),
            self.read_modbus_data_hc3_foreruntemperature(),
            self.read_modbus_data_hc3_returnflowtemperature(),
            self.read_modbus_data_bufferstorage_status(),
            self.read_modbus_data_bufferstorage1_temperature_top(),
            self.read_modbus_data_bufferstorage1_temperature_middletop(),
            self.read_modbus_data_bufferstorage1_temperature_middlebottom(),
            self.read_modbus_data_bufferstorage1_temperature_bottom(),
            self.read_modbus_data_bufferstorage2_temperature_top(),
            self.read_modbus_data_bufferstorage2_temperature_middletop(),
            self.read_modbus_data_bufferstorage2_temperature_middlebottom(),
            self.read_modbus_data_bufferstorage2_temperature_bottom(),
            self.read_modbus_data_bufferstorage_chargeswitchmixerstatus(),
            self.read_modbus_data_bufferstorage_chargeswitchmixernormed(),
            self.read_modbus_data_bufferstorage_chargeswitchmixerposition(),
            self.read_modbus_data_bufferstorage_chargepumpstatus(),
            self.read_modbus_data_bufferstorage_temperature_chargewater(),
            self.read_modbus_data_bufferstorage1_filllevel(),
            self.read_modbus_data_bufferstorage2_filllevel(),
            self.read_modbus_data_bufferstorage_combined_filllevel(),
            self.read_modbus_data_bufferstorage_activestatus(),
            self.read_modbus_data_warmwater_boiler_status(),
            self.read_modbus_data_warmwater_boiler_watertemperature(),
            self.read_modbus_data_warmwater_boiler_chargepumpstatus(),
            self.read_modbus_data_warmwater_boiler_valvestatus(),
            self.read_modbus_data_warmwater_bath_heatingactive(),
            self.read_modbus_data_woodburner_status(),
            self.read_modbus_data_woodburner_exhausttemperature(),
            self.read_modbus_data_woodburner_watertemperature()
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

        if temperature_raw == 0x7FFD:
            self.data["outsidetemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["outsidetemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
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

        if temperature_raw == 0x7FFD:
            self.data["room1temperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["room1temperature"] = "Init"
        elif temperature_raw == 0x7FFF:
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

        if temperature_raw == 0x7FFD:
            self.data["room2temperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["room2temperature"] = "Init"
        elif temperature_raw == 0x7FFF:
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

        if doorbellstatus == 0:
            self.data["doorbell_status"] = "Nicht verbaut"
        elif doorbellstatus == 1:
            self.data["doorbell_status"] = "Aus"
        elif doorbellstatus == 2:
            self.data["doorbell_status"] = "An"
        elif doorbellstatus == 3:
            self.data["doorbell_status"] = "Fehler"
        else:
            self.data["doorbell_status"] = None
        
        return True
    
    def read_modbus_data_heatcontrolmanagement_enabled(self, start_address=30):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["heatcontrolmanagement_enabled"] = decoder.decode_16bit_uint() != 0
        
        return True
    
    def read_modbus_data_heatcontrolmanagement_belowmintemperature(self, start_address=31):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["heatcontrolmanagement_lowTemperatureWarning"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_hc1_status(self, start_address=40):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_1_status"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_1_status"] = "Aus - Manuell"
        elif status == 2:
            self.data["heatcircuit_1_status"] = "Aus - Timer"
        elif status == 3:
            self.data["heatcircuit_1_status"] = "Nachtbetrieb - Manuell"
        elif status == 4:
            self.data["heatcircuit_1_status"] = "Nachtbetrieb - Timer"
        elif status == 5:
            self.data["heatcircuit_1_status"] = "Tagbetrieb - Manuell"
        elif status == 6:
            self.data["heatcircuit_1_status"] = "Tagbetrieb - Timer"
        elif status == 7:
            self.data["heatcircuit_1_status"] = "Fehler"
        else:
            self.data["heatcircuit_1_status"] = None
        
        return True

    def read_modbus_data_hc1_pumpstatus(self, start_address=41):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_1_pumpstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_1_pumpstatus"] = "Aus"
        elif status == 2:
            self.data["heatcircuit_1_pumpstatus"] = "An"
        elif status == 3:
            self.data["heatcircuit_1_pumpstatus"] = "Fehler"
        else:
            self.data["heatcircuit_1_pumpstatus"] = None
        
        return True

    def read_modbus_data_hc1_mixerstatus(self, start_address=42):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_1_mixerstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_1_mixerstatus"] = "Aus"
        elif status == 2:
            self.data["heatcircuit_1_mixerstatus"] = "Normierung"
        elif status == 3:
            self.data["heatcircuit_1_mixerstatus"] = "Öffen - Langsam"
        elif status == 4:
            self.data["heatcircuit_1_mixerstatus"] = "Öffnen - Schnell"
        elif status == 5:
            self.data["heatcircuit_1_mixerstatus"] = "Schließen - Langsam"
        elif status == 6:
            self.data["heatcircuit_1_mixerstatus"] = "Schließen - Schnell"
        elif status == 7:
            self.data["heatcircuit_1_mixerstatus"] = "Fehler"
        else:
            self.data["heatcircuit_1_mixerstatus"] = None
        
        return True
    
    def read_modbus_data_hc1_mixernormed(self, start_address=43):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["heatcircuit_1_mixernormed"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_hc1_mixerposition(self, start_address=44):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        position = decoder.decode_16bit_uint()

        if position > 100:
            self.data["heatcircuit_1_mixerposition"] = None
        else:
            self.data["heatcircuit_1_mixerposition"] = position
        
        return True

    def read_modbus_data_hc1_targetforeruntemperature(self, start_address=45):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature = decoder.decode_16bit_uint()

        if temperature > 100:
            self.data["heatcircuit_1_targetForerunTemperature"] = None
        else:
            self.data["heatcircuit_1_targetForerunTemperature"] = temperature
        
        return True

    def read_modbus_data_hc1_foreruntemperature(self, start_address=46):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["heatcircuit_1_forerunTemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["heatcircuit_1_forerunTemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["heatcircuit_1_forerunTemperature"] = "Fehler"
        else:
            self.data["heatcircuit_1_forerunTemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_hc1_returnflowtemperature(self, start_address=47):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["heatcircuit_1_returnflowTemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["heatcircuit_1_returnflowTemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["heatcircuit_1_returnflowTemperature"] = "Fehler"
        else:
            self.data["heatcircuit_1_returnflowTemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_hc2_status(self, start_address=60):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_2_status"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_2_status"] = "Aus - Manuell"
        elif status == 2:
            self.data["heatcircuit_2_status"] = "Aus - Timer"
        elif status == 3:
            self.data["heatcircuit_2_status"] = "Nachtbetrieb - Manuell"
        elif status == 4:
            self.data["heatcircuit_2_status"] = "Nachtbetrieb - Timer"
        elif status == 5:
            self.data["heatcircuit_2_status"] = "Tagbetrieb - Manuell"
        elif status == 6:
            self.data["heatcircuit_2_status"] = "Tagbetrieb - Timer"
        elif status == 7:
            self.data["heatcircuit_2_status"] = "Fehler"
        else:
            self.data["heatcircuit_2_status"] = None
        
        return True

    def read_modbus_data_hc2_pumpstatus(self, start_address=61):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_2_pumpstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_2_pumpstatus"] = "Aus"
        elif status == 2:
            self.data["heatcircuit_2_pumpstatus"] = "An"
        elif status == 3:
            self.data["heatcircuit_2_pumpstatus"] = "Fehler"
        else:
            self.data["heatcircuit_2_pumpstatus"] = None
        
        return True

    def read_modbus_data_hc2_mixerstatus(self, start_address=62):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_2_mixerstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_2_mixerstatus"] = "Aus"
        elif status == 2:
            self.data["heatcircuit_2_mixerstatus"] = "Normierung"
        elif status == 3:
            self.data["heatcircuit_2_mixerstatus"] = "Öffen - Langsam"
        elif status == 6:
            self.data["heatcircuit_2_mixerstatus"] = "Öffnen - Schnell"
        elif status == 5:
            self.data["heatcircuit_2_mixerstatus"] = "Schließen - Langsam"
        elif status == 6:
            self.data["heatcircuit_2_mixerstatus"] = "Schließen - Schnell"
        elif status == 7:
            self.data["heatcircuit_2_mixerstatus"] = "Fehler"
        else:
            self.data["heatcircuit_2_mixerstatus"] = None
        
        return True
    
    def read_modbus_data_hc2_mixernormed(self, start_address=63):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["heatcircuit_2_mixernormed"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_hc2_mixerposition(self, start_address=64):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        position = decoder.decode_16bit_uint()

        if position > 100:
            self.data["heatcircuit_2_mixerposition"] = None
        else:
            self.data["heatcircuit_2_mixerposition"] = position
        
        return True

    def read_modbus_data_hc2_targetforeruntemperature(self, start_address=65):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature = decoder.decode_16bit_uint()

        if temperature > 100:
            self.data["heatcircuit_2_targetForerunTemperature"] = None
        else:
            self.data["heatcircuit_2_targetForerunTemperature"] = temperature
        
        return True

    def read_modbus_data_hc2_foreruntemperature(self, start_address=66):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["heatcircuit_2_forerunTemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["heatcircuit_2_forerunTemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["heatcircuit_2_forerunTemperature"] = "Fehler"
        else:
            self.data["heatcircuit_2_forerunTemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_hc2_returnflowtemperature(self, start_address=67):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["heatcircuit_2_returnflowTemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["heatcircuit_2_returnflowTemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["heatcircuit_2_returnflowTemperature"] = "Fehler"
        else:
            self.data["heatcircuit_2_returnflowTemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_hc3_status(self, start_address=80):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_3_status"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_3_status"] = "Aus - Manuell"
        elif status == 2:
            self.data["heatcircuit_3_status"] = "Aus - Timer"
        elif status == 3:
            self.data["heatcircuit_3_status"] = "Nachtbetrieb - Manuell"
        elif status == 4:
            self.data["heatcircuit_3_status"] = "Nachtbetrieb - Timer"
        elif status == 5:
            self.data["heatcircuit_3_status"] = "Tagbetrieb - Manuell"
        elif status == 6:
            self.data["heatcircuit_3_status"] = "Tagbetrieb - Timer"
        elif status == 7:
            self.data["heatcircuit_3_status"] = "Fehler"
        else:
            self.data["heatcircuit_3_status"] = None
        
        return True

    def read_modbus_data_hc3_pumpstatus(self, start_address=81):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_3_pumpstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_3_pumpstatus"] = "Aus"
        elif status == 2:
            self.data["heatcircuit_3_pumpstatus"] = "An"
        elif status == 3:
            self.data["heatcircuit_3_pumpstatus"] = "Fehler"
        else:
            self.data["heatcircuit_3_pumpstatus"] = None
        
        return True

    def read_modbus_data_hc3_mixerstatus(self, start_address=82):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["heatcircuit_3_mixerstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["heatcircuit_3_mixerstatus"] = "Aus"
        elif status == 2:
            self.data["heatcircuit_3_mixerstatus"] = "Normierung"
        elif status == 3:
            self.data["heatcircuit_3_mixerstatus"] = "Öffen - Langsam"
        elif status == 4:
            self.data["heatcircuit_3_mixerstatus"] = "Öffnen - Schnell"
        elif status == 5:
            self.data["heatcircuit_3_mixerstatus"] = "Schließen - Langsam"
        elif status == 6:
            self.data["heatcircuit_3_mixerstatus"] = "Schließen - Schnell"
        elif status == 7:
            self.data["heatcircuit_3_mixerstatus"] = "Fehler"
        else:
            self.data["heatcircuit_3_mixerstatus"] = None
        
        return True
    
    def read_modbus_data_hc3_mixernormed(self, start_address=83):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["heatcircuit_3_mixernormed"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_hc3_mixerposition(self, start_address=84):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        position = decoder.decode_16bit_uint()

        if position > 100:
            self.data["heatcircuit_3_mixerposition"] = None
        else:
            self.data["heatcircuit_3_mixerposition"] = position
        
        return True

    def read_modbus_data_hc3_targetforeruntemperature(self, start_address=85):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature = decoder.decode_16bit_uint()

        if temperature > 100:
            self.data["heatcircuit_3_targetForerunTemperature"] = None
        else:
            self.data["heatcircuit_3_targetForerunTemperature"] = temperature
        
        return True

    def read_modbus_data_hc3_foreruntemperature(self, start_address=86):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["heatcircuit_3_forerunTemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["heatcircuit_3_forerunTemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["heatcircuit_3_forerunTemperature"] = "Fehler"
        else:
            self.data["heatcircuit_3_forerunTemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_hc3_returnflowtemperature(self, start_address=87):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["heatcircuit_3_returnflowTemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["heatcircuit_3_returnflowTemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["heatcircuit_3_returnflowTemperature"] = "Fehler"
        else:
            self.data["heatcircuit_3_returnflowTemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage_status(self, start_address=100):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["bufferstorage_status"] = "Nicht verbaut"
        elif status == 1:
            self.data["bufferstorage_status"] = "OK"
        elif status == 2:
            self.data["bufferstorage_status"] = "Kodierfehler"
        elif status == 3:
            self.data["bufferstorage_status"] = "Temperatursensorfehler"
        elif status == 4:
            self.data["bufferstorage_status"] = "Externer Fehler"
        else:
            self.data["bufferstorage_status"] = None
        
        return True

    def read_modbus_data_bufferstorage1_temperature_top(self, start_address=101):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_1_temperature_top"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_1_temperature_top"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_1_temperature_top"] = "Fehler"
        else:
            self.data["bufferstorage_1_temperature_top"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage1_temperature_middletop(self, start_address=102):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_1_temperature_middletop"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_1_temperature_middletop"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_1_temperature_middletop"] = "Fehler"
        else:
            self.data["bufferstorage_1_temperature_middletop"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage1_temperature_middlebottom(self, start_address=103):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_1_temperature_middlebottom"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_1_temperature_middlebottom"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_1_temperature_middlebottom"] = "Fehler"
        else:
            self.data["bufferstorage_1_temperature_middlebottom"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage1_temperature_bottom(self, start_address=104):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_1_temperature_bottom"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_1_temperature_bottom"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_1_temperature_bottom"] = "Fehler"
        else:
            self.data["bufferstorage_1_temperature_bottom"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage2_temperature_top(self, start_address=105):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_2_temperature_top"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_2_temperature_top"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_2_temperature_top"] = "Fehler"
        else:
            self.data["bufferstorage_2_temperature_top"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage2_temperature_middletop(self, start_address=106):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_2_temperature_middletop"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_2_temperature_middletop"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_2_temperature_middletop"] = "Fehler"
        else:
            self.data["bufferstorage_2_temperature_middletop"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage2_temperature_middlebottom(self, start_address=107):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_2_temperature_middlebottom"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_2_temperature_middlebottom"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_2_temperature_middlebottom"] = "Fehler"
        else:
            self.data["bufferstorage_2_temperature_middlebottom"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage2_temperature_bottom(self, start_address=108):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_2_temperature_bottom"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_2_temperature_bottom"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_2_temperature_bottom"] = "Fehler"
        else:
            self.data["bufferstorage_2_temperature_bottom"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage_chargeswitchmixerstatus(self, start_address=109):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Aus"
        elif status == 2:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Normierung"
        elif status == 3:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Öffen - Langsam"
        elif status == 4:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Öffnen - Schnell"
        elif status == 5:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Schließen - Langsam"
        elif status == 6:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Schließen - Schnell"
        elif status == 7:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = "Fehler"
        else:
            self.data["bufferstorage_charge_or_switch_mixerstatus"] = None
        
        return True
    
    def read_modbus_data_bufferstorage_chargeswitchmixernormed(self, start_address=110):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["bufferstorage_charge_or_switch_mixernormed"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_bufferstorage_chargeswitchmixerposition(self, start_address=111):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        position = decoder.decode_16bit_uint()

        if position > 100:
            self.data["bufferstorage_charge_or_switch_mixerposition"] = None
        else:
            self.data["bufferstorage_charge_or_switch_mixerposition"] = position
        
        return True

    def read_modbus_data_bufferstorage_chargepumpstatus(self, start_address=112):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["bufferstorage_chargepumpstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["bufferstorage_chargepumpstatus"] = "Aus"
        elif status == 2:
            self.data["bufferstorage_chargepumpstatus"] = "An"
        elif status == 3:
            self.data["bufferstorage_chargepumpstatus"] = "Fehler"
        else:
            self.data["bufferstorage_chargepumpstatus"] = None
        
        return True

    def read_modbus_data_bufferstorage_temperature_chargewater(self, start_address=113):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["bufferstorage_chargewatertemperature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["bufferstorage_chargewatertemperature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["bufferstorage_chargewatertemperature"] = "Fehler"
        else:
            self.data["bufferstorage_chargewatertemperature"] = temperature_raw/10
        
        return True

    def read_modbus_data_bufferstorage1_filllevel(self, start_address=114):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        filllevel = decoder.decode_16bit_uint()

        if filllevel == 0xFFFF:
            self.data["bufferstorage_1_filllevel"] = "Ungültig"
        else:
            self.data["bufferstorage_1_filllevel"] = filllevel/10
        
        return True

    def read_modbus_data_bufferstorage2_filllevel(self, start_address=115):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        filllevel = decoder.decode_16bit_uint()

        if filllevel == 0xFFFE:
            self.data["bufferstorage_2_filllevel"] = "Nicht verbaut"
        elif filllevel == 0xFFFF:
            self.data["bufferstorage_2_filllevel"] = "Ungültig"
        else:
            self.data["bufferstorage_2_filllevel"] = filllevel/10
        
        return True

    def read_modbus_data_bufferstorage_combined_filllevel(self, start_address=116):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        filllevel = decoder.decode_16bit_uint()

        if filllevel == 0xFFFF:
            self.data["bufferstorage_combined_filllevel"] = "Ungültig"
        else:
            self.data["bufferstorage_combined_filllevel"] = filllevel/10
        
        return True

    def read_modbus_data_bufferstorage_activestatus(self, start_address=117):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["bufferstorage_active_status"] = "Nicht verfügbar"
        elif status == 1:
            self.data["bufferstorage_active_status"] = "Pufferspeicher 1"
        elif status == 2:
            self.data["bufferstorage_active_status"] = "Pufferspeicher 2"
        elif status == 3:
            self.data["bufferstorage_active_status"] = "Beide parallel"
        else:
            self.data["bufferstorage_active_status"] = None
        
        return True

    def read_modbus_data_warmwater_boiler_status(self, start_address=140):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["warmwater_boiler_status"] = "Nicht verfügbar"
        elif status == 1:
            self.data["warmwater_boiler_status"] = "Aus"
        elif status == 2:
            self.data["warmwater_boiler_status"] = "manuelles laden"
        elif status == 3:
            self.data["warmwater_boiler_status"] = "automatisches laden"
        elif status == 4:
            self.data["warmwater_boiler_status"] = "laden wird beendet"
        elif status == 5:
            self.data["warmwater_boiler_status"] = "Fehler: Ladevorgang Zeitüberschreitung"
        elif status == 6:
            self.data["warmwater_boiler_status"] = "Fehler"
        else:
            self.data["warmwater_boiler_status"] = None
        
        return True

    def read_modbus_data_warmwater_boiler_watertemperature(self, start_address=141):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["warmwater_boiler_temerature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["warmwater_boiler_temerature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["warmwater_boiler_temerature"] = "Fehler"
        else:
            self.data["warmwater_boiler_temerature"] = temperature_raw/10
        
        return True

    def read_modbus_data_warmwater_boiler_chargepumpstatus(self, start_address=142):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["warmwater_boiler_chargepumpstatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["warmwater_boiler_chargepumpstatus"] = "Aus"
        elif status == 2:
            self.data["warmwater_boiler_chargepumpstatus"] = "An"
        elif status == 3:
            self.data["warmwater_boiler_chargepumpstatus"] = "Fehler"
        else:
            self.data["warmwater_boiler_chargepumpstatus"] = None
        
        return True

    def read_modbus_data_warmwater_boiler_valvestatus(self, start_address=143):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["warmwater_boiler_valvestatus"] = "Nicht verbaut"
        elif status == 1:
            self.data["warmwater_boiler_valvestatus"] = "Entnormiert"
        elif status == 2:
            self.data["warmwater_boiler_valvestatus"] = "Offen"
        elif status == 3:
            self.data["warmwater_boiler_valvestatus"] = "Öffnen"
        elif status == 4:
            self.data["warmwater_boiler_valvestatus"] = "Geschlossen"
        elif status == 5:
            self.data["warmwater_boiler_valvestatus"] = "Schließen"
        elif status == 6:
            self.data["warmwater_boiler_valvestatus"] = "Fehler"
        else:
            self.data["warmwater_boiler_valvestatus"] = None
        
        return True
    
    def read_modbus_data_warmwater_bath_heatingactive(self, start_address=144):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["warmwater_bath_heatingactive"] = decoder.decode_16bit_uint() != 0
        
        return True

    def read_modbus_data_woodburner_status(self, start_address=160):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        status = decoder.decode_16bit_uint()

        if status == 0:
            self.data["woodburner_status"] = "Nicht verfügbar"
        elif status == 1:
            self.data["woodburner_status"] = "Aus"
        elif status == 2:
            self.data["woodburner_status"] = "Pumpe aktiv"
        elif status == 3:
            self.data["woodburner_status"] = "Brand Startphase"
        elif status == 4:
            self.data["woodburner_status"] = "Brand Startphase fehlgeschlagen"
        elif status == 5:
            self.data["woodburner_status"] = "Brennt"
        elif status == 6:
            self.data["woodburner_status"] = "Brennvorgang beendet"
        elif status == 7:
            self.data["woodburner_status"] = "Fehler - Stromversorgung unterbrochen"
        elif status == 8:
            self.data["woodburner_status"] = "Fehler"
        else:
            self.data["woodburner_status"] = None
        
        return True

    def read_modbus_data_woodburner_exhausttemperature(self, start_address=161):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["woodburner_exhaust_temerature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["woodburner_exhaust_temerature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["woodburner_exhaust_temerature"] = "Fehler"
        else:
            self.data["woodburner_exhaust_temerature"] = temperature_raw/10
        
        return True

    def read_modbus_data_woodburner_watertemperature(self, start_address=162):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)

        temperature_raw = decoder.decode_16bit_int()

        if temperature_raw == 0x7FFD:
            self.data["woodburner_water_temerature"] = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            self.data["woodburner_water_temerature"] = "Init"
        elif temperature_raw == 0x7FFF:
            self.data["woodburner_water_temerature"] = "Fehler"
        else:
            self.data["woodburner_water_temerature"] = temperature_raw/10
        
        return True