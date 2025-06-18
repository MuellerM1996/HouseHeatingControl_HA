import logging
import threading
from typing import Optional
from datetime import timedelta, datetime

import pymodbus
from pymodbus.client import ModbusTcpClient

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval

from .const import DEFAULT_MODBUS_TIMEOUT

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
        self._readout_active = False
        self._name = name
        self._address = address
        self._scan_interval = timedelta(seconds=scan_interval)
        self._last_data_received_timestamp = datetime(year=2000, month=1, day=1)
        self._unsub_interval_method = None
        self._sensors = []
            
    @callback
    def async_add_homeheatcontrol_sensor(self, sensor):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )
        self._sensors.append(sensor)

    @callback
    def async_remove_homeheatcontrol_sensor(self, sensor):
        """Remove data update."""
        self._sensors.remove(sensor)

        if not self._sensors:
            """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()

    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> dict:
        """Time to update."""
        result : bool = await self._hass.async_add_executor_job(self._refresh_modbus_data)
        if result:
            self._last_data_received_timestamp = datetime.now()
            for sensor in self._sensors:
                _modbus_data_updated = getattr(sensor, "_modbus_data_updated", None)
                if callable(_modbus_data_updated):
                    sensor._modbus_data_updated()
        
        if (datetime.now() - self._last_data_received_timestamp).total_seconds() > DEFAULT_MODBUS_TIMEOUT:
            #set all data to None so entities get unavailable
            for sensor in self._sensors:
                _data = getattr(sensor, "_data", None)
                if _data is not None:
                    sensor._data = None
                _modbus_data_updated = getattr(sensor, "_modbus_data_updated", None)
                if callable(_modbus_data_updated):
                    sensor._modbus_data_updated()

    def _refresh_modbus_data(self, _now: Optional[int] = None) -> bool:
        """Time to update."""
        if not self._sensors:
            return False

        if not self._check_and_reconnect():
            #if not connected, skip
            return False

        #check if readout is currently active
        if self._readout_active == True:
            return False
        
        #lock read modbus
        self._readout_active = True
        try:
            update_result = self.read_modbus_data()
        except Exception as e:
            _LOGGER.exception("Error reading modbus data", exc_info=True)
            update_result = False

        #unlock read modbus
        self._readout_active = False

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
    
    def get_sensor_by_name(self, name: str):
        for i in range(len(self._sensors)):
            try:
                if name in self._sensors[i].entity_description.key:
                    return self._sensors[i]
            except:
                pass
        return None
            
    def read_modbus_data(self):
        _LOGGER.debug("Modbus read Start")
        result = False
        try:
            result = (
                self.read_modbus_data_sw_Version(),
                self.read_modbus_data_bool(self.get_sensor_by_name("dtcactive")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("outsidetemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("room1temperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("room2temperature")),
                self.read_modbus_data_doorbellstatus(),
                self.read_modbus_data_bool(self.get_sensor_by_name("heatcontrolmanagement_enabled")),
                self.read_modbus_data_bool(self.get_sensor_by_name("heatcontrolmanagement_lowTemperatureWarning")),
                self.read_modbus_data_hc_status(self.get_sensor_by_name("heatcircuit_1_status")),
                self.read_modbus_data_pumpstatus(self.get_sensor_by_name("heatcircuit_1_pumpstatus")),
                self.read_modbus_data_mixerstatus(self.get_sensor_by_name("heatcircuit_1_mixerstatus")),
                self.read_modbus_data_bool(self.get_sensor_by_name("heatcircuit_1_mixernormed")),
                self.read_modbus_data_mixerposition(self.get_sensor_by_name("heatcircuit_1_mixerposition")),
                self.read_modbus_data_hc_targetforeruntemperature(self.get_sensor_by_name("heatcircuit_1_targetForerunTemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("heatcircuit_1_forerunTemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("heatcircuit_1_returnflowTemperature")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_mode_overwrite")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_timer_1_mode")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_timer_1_start")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_timer_1_stop")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_timer_2_mode")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_timer_2_start")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_timer_2_stop")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_curve_inclination")),
                self.read_modbus_data_signed16bit(self.get_sensor_by_name("heatcircuit_1_curve_niveau")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_curve_targettemperature_day")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_1_curve_targettemperature_night")),
                self.read_modbus_data_hc_status(self.get_sensor_by_name("heatcircuit_2_status")),
                self.read_modbus_data_pumpstatus(self.get_sensor_by_name("heatcircuit_2_pumpstatus")),
                self.read_modbus_data_mixerstatus(self.get_sensor_by_name("heatcircuit_2_mixerstatus")),
                self.read_modbus_data_bool(self.get_sensor_by_name("heatcircuit_2_mixernormed")),
                self.read_modbus_data_mixerposition(self.get_sensor_by_name("heatcircuit_2_mixerposition")),
                self.read_modbus_data_hc_targetforeruntemperature(self.get_sensor_by_name("heatcircuit_2_targetForerunTemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("heatcircuit_2_forerunTemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("heatcircuit_2_returnflowTemperature")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_mode_overwrite")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_timer_1_mode")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_timer_1_start")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_timer_1_stop")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_timer_2_mode")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_timer_2_start")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_timer_2_stop")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_curve_inclination")),
                self.read_modbus_data_signed16bit(self.get_sensor_by_name("heatcircuit_2_curve_niveau")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_curve_targettemperature_day")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_2_curve_targettemperature_night")),
                self.read_modbus_data_hc_status(self.get_sensor_by_name("heatcircuit_3_status")),
                self.read_modbus_data_pumpstatus(self.get_sensor_by_name("heatcircuit_3_pumpstatus")),
                self.read_modbus_data_mixerstatus(self.get_sensor_by_name("heatcircuit_3_mixerstatus")),
                self.read_modbus_data_bool(self.get_sensor_by_name("heatcircuit_3_mixernormed")),
                self.read_modbus_data_mixerposition(self.get_sensor_by_name("heatcircuit_3_mixerposition")),
                self.read_modbus_data_hc_targetforeruntemperature(self.get_sensor_by_name("heatcircuit_3_targetForerunTemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("heatcircuit_3_forerunTemperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("heatcircuit_3_returnflowTemperature")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_mode_overwrite")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_timer_1_mode")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_timer_1_start")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_timer_1_stop")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_timer_2_mode")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_timer_2_start")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_timer_2_stop")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_curve_inclination")),
                self.read_modbus_data_signed16bit(self.get_sensor_by_name("heatcircuit_3_curve_niveau")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_curve_targettemperature_day")),
                self.read_modbus_data_unsigned16bit(self.get_sensor_by_name("heatcircuit_3_curve_targettemperature_night")),
                self.read_modbus_data_bufferstorage_status(),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_1_temperature_top")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_1_temperature_middletop")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_1_temperature_middlebottom")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_1_temperature_bottom")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_2_temperature_top")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_2_temperature_middletop")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_2_temperature_middlebottom")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_2_temperature_bottom")),
                self.read_modbus_data_mixerstatus(self.get_sensor_by_name("bufferstorage_charge_or_switch_mixerstatus")),
                self.read_modbus_data_bool(self.get_sensor_by_name("bufferstorage_charge_or_switch_mixernormed")),
                self.read_modbus_data_mixerposition(self.get_sensor_by_name("bufferstorage_charge_or_switch_mixerposition")),
                self.read_modbus_data_pumpstatus(self.get_sensor_by_name("bufferstorage_chargepumpstatus")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("bufferstorage_chargewatertemperature")),
                self.read_modbus_data_bufferstorage_filllevel(self.get_sensor_by_name("bufferstorage_1_filllevel")),
                self.read_modbus_data_bufferstorage_filllevel(self.get_sensor_by_name("bufferstorage_2_filllevel")),
                self.read_modbus_data_bufferstorage_filllevel(self.get_sensor_by_name("bufferstorage_combined_filllevel")),
                self.read_modbus_data_bufferstorage_activestatus(),
                self.read_modbus_data_valvestatus(self.get_sensor_by_name("bufferstorage_chargevalvestatus")),
                self.read_modbus_data_bufferstorage_chargestatus(),
                self.read_modbus_data_bool(self.get_sensor_by_name("bufferstorage_chargeElectricOnly")),
                self.read_modbus_data_warmwater_boiler_status(),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("warmwater_boiler_temperature")),
                self.read_modbus_data_pumpstatus(self.get_sensor_by_name("warmwater_boiler_chargepumpstatus")),
                self.read_modbus_data_valvestatus(self.get_sensor_by_name("warmwater_boiler_valvestatus")),
                self.read_modbus_data_bool(self.get_sensor_by_name("warmwater_bath_heatingactive")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("warmwater_circulation_outputtemperature")),
                self.read_modbus_data_pumpstatus(self.get_sensor_by_name("warmwater_circulation_pumpstatus")),
                self.read_modbus_data_warmwater_circulation_circuit_status(self.get_sensor_by_name("warmwater_circulation_circuit1_status")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("warmwater_circulation_circuit1_temperature")),
                self.read_modbus_data_valvestatus(self.get_sensor_by_name("warmwater_circulation_circuit1_valvestatus")),
                self.read_modbus_data_warmwater_circulation_circuit_status(self.get_sensor_by_name("warmwater_circulation_circuit2_status")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("warmwater_circulation_circuit2_temperature")),
                self.read_modbus_data_valvestatus(self.get_sensor_by_name("warmwater_circulation_circuit2_valvestatus")),
                self.read_modbus_data_woodburner_status(),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("woodburner_exhaust_temperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("woodburner_water_temperature")),
                self.read_modbus_data_gasburner_status(),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("gasburner_exhaust_temperature")),
                self.read_modbus_data_temperaturesensor_signed16bit(self.get_sensor_by_name("gasburner_water_temperature")),
            )
        except (BrokenPipeError, pymodbus.exceptions.ModbusIOException):
            self.close()

        _LOGGER.debug("Modbus read End")
        return result

    def read_modbus_data_sw_Version(self):
        """start reading data"""
        sensor_fbl = self.get_sensor_by_name("fbl_sw_version")
        sensor_appl = self.get_sensor_by_name("appl_sw_version")
        data_package = self.read_holding_registers(unit=sensor_fbl._slaveId, address=sensor_fbl._address, count=4)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor_fbl._address} Name:{sensor_fbl.entity_description.key}')
            return False
        value = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT64)
        
        fbl_sw_version_major = value >> 56
        fbl_sw_version_minor = (value >> 48) & 0xFF
        fbl_sw_version_patch = (value >> 40) & 0xFF
        appl_sw_version_major = (value >> 32) & 0xFF
        appl_sw_version_minor = (value >> 24) & 0xFF
        appl_sw_version_patch = (value >> 16) & 0xFF

        sensor_fbl._data = f"{fbl_sw_version_major}.{fbl_sw_version_minor}.{fbl_sw_version_patch}"
        sensor_appl._data = f"{appl_sw_version_major}.{appl_sw_version_minor}.{appl_sw_version_patch}"
        
        return True
    
    def read_modbus_data_bool(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False
        
        sensor._data = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16) != 0

        return True
    
    def read_modbus_data_unsigned16bit(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False
        
        sensor._data = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        return True
    
    def read_modbus_data_signed16bit(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False
        
        sensor._data = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.INT16)

        return True
    
    def read_modbus_data_temperaturesensor_signed16bit(self, sensor):
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        temperature_raw = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.INT16)

        if temperature_raw == 0x7FFD:
            sensor._data = "Nicht verbaut"
        elif temperature_raw == 0x7FFE:
            sensor._data = "Init"
        elif temperature_raw == 0x7FFF:
            sensor._data = "Fehler"
        else:
            sensor._data = temperature_raw/10
        
        return True

    def read_modbus_data_pumpstatus(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verbaut"
        elif status == 1:
            sensor._data = "Aus"
        elif status == 2:
            sensor._data = "An"
        elif status == 3:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_mixerstatus(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verbaut"
        elif status == 1:
            sensor._data = "Aus"
        elif status == 2:
            sensor._data = "Normierung"
        elif status == 3:
            sensor._data = "Öffen - Langsam"
        elif status == 4:
            sensor._data = "Öffnen - Schnell"
        elif status == 5:
            sensor._data = "Schließen - Langsam"
        elif status == 6:
            sensor._data = "Schließen - Schnell"
        elif status == 7:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_mixerposition(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        position = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if position > 100:
            sensor._data = None
        else:
            sensor._data = position
        
        return True

    def read_modbus_data_valvestatus(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verbaut"
        elif status == 1:
            sensor._data = "Entnormiert"
        elif status == 2:
            sensor._data = "Offen"
        elif status == 3:
            sensor._data = "Öffnen"
        elif status == 4:
            sensor._data = "Geschlossen"
        elif status == 5:
            sensor._data = "Schließen"
        elif status == 6:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_hc_status(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verbaut"
        elif status == 1:
            sensor._data = "Aus - Manuell"
        elif status == 2:
            sensor._data = "Aus - Timer"
        elif status == 3:
            sensor._data = "Nachtbetrieb - Manuell"
        elif status == 4:
            sensor._data = "Nachtbetrieb - Timer"
        elif status == 5:
            sensor._data = "Tagbetrieb - Manuell"
        elif status == 6:
            sensor._data = "Tagbetrieb - Timer"
        elif status == 7:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_hc_targetforeruntemperature(self, sensor):
        """at the moment the datahandling is the same as for the mixer position"""
        return self.read_modbus_data_mixerposition(sensor)

    def read_modbus_data_doorbellstatus(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("doorbell_status")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        doorbellstatus = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if doorbellstatus == 0:
            sensor._data = "Nicht verbaut"
        elif doorbellstatus == 1:
            sensor._data = "Aus"
        elif doorbellstatus == 2:
            sensor._data = "An"
        elif doorbellstatus == 3:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_bufferstorage_status(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("bufferstorage_status")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verbaut"
        elif status == 1:
            sensor._data = "OK"
        elif status == 2:
            sensor._data = "Kodierfehler"
        elif status == 3:
            sensor._data = "Temperatursensorfehler"
        elif status == 4:
            sensor._data = "Externer Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_bufferstorage_filllevel(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        filllevel = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if filllevel == 0xFFFE:
            sensor._data = "Nicht verbaut"
        elif filllevel == 0xFFFF:
            sensor._data = "Ungültig"
        else:
            sensor._data = filllevel/10
        
        return True

    def read_modbus_data_bufferstorage_activestatus(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("bufferstorage_active_status")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verfügbar"
        elif status == 1:
            sensor._data = "Pufferspeicher 1"
        elif status == 2:
            sensor._data = "Pufferspeicher 2"
        elif status == 3:
            sensor._data = "Beide parallel"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_bufferstorage_chargestatus(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("bufferstorage_chargestatus")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verfügbar"
        elif status == 1:
            sensor._data = "Nicht aktiv"
        elif status == 2:
            sensor._data = "Aktiv"
        elif status == 3:
            sensor._data = "Überladen aktiv"
        elif status == 4:
            sensor._data = "Vollständig überladen"
        elif status == 5:
            sensor._data = "Angefordert"
        elif status == 6:
            sensor._data = "Nachlauf"
        elif status == 7:
            sensor._data = "Fehler Temperatursensor"
        elif status == 8:
            sensor._data = "Fehler Extern"
        elif status == 9:
            sensor._data = "Fehler Kodierung"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_warmwater_boiler_status(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("warmwater_boiler_status")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verfügbar"
        elif status == 1:
            sensor._data = "Aus"
        elif status == 2:
            sensor._data = "manuelles laden"
        elif status == 3:
            sensor._data = "automatisches laden"
        elif status == 4:
            sensor._data = "laden wird beendet"
        elif status == 5:
            sensor._data = "Fehler: Ladevorgang Zeitüberschreitung"
        elif status == 6:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_warmwater_circulation_circuit_status(self, sensor):
        """start reading data"""
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verbaut"
        elif status == 1:
            sensor._data = "Aus"
        elif status == 2:
            sensor._data = "An"
        elif status == 3:
            sensor._data = "Fehler Kodierung"
        elif status == 4:
            sensor._data = "Fehler Temperatursensor"
        elif status == 5:
            sensor._data = "Fehler Pumpe oder Ventil"
        elif status == 6:
            sensor._data = "Fehler Extern"
        elif status == 7:
            sensor._data = "Fehler Pufferspeicher unter Mindesttemperatur"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_woodburner_status(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("woodburner_status")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verfügbar"
        elif status == 1:
            sensor._data = "Aus"
        elif status == 2:
            sensor._data = "Pumpe aktiv"
        elif status == 3:
            sensor._data = "Brand Startphase"
        elif status == 4:
            sensor._data = "Brand Startphase fehlgeschlagen"
        elif status == 5:
            sensor._data = "Brennt"
        elif status == 6:
            sensor._data = "Brennvorgang beendet"
        elif status == 7:
            sensor._data = "Fehler - Stromversorgung unterbrochen"
        elif status == 8:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True

    def read_modbus_data_gasburner_status(self):
        """start reading data"""
        sensor = self.get_sensor_by_name("gasburner_status")
        data_package = self.read_holding_registers(unit=sensor._slaveId, address=sensor._address, count=1)      
        if data_package.isError():
            _LOGGER.debug(f'Data error at start address:{sensor._address} Name:{sensor.entity_description.key}')
            return False

        status = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)

        if status == 0:
            sensor._data = "Nicht verfügbar"
        elif status == 1:
            sensor._data = "Aus"
        elif status == 2:
            sensor._data = "Pumpe aktiv"
        elif status == 3:
            sensor._data = "Brand Startphase"
        elif status == 4:
            sensor._data = "Brand Startphase fehlgeschlagen"
        elif status == 5:
            sensor._data = "Brennt"
        elif status == 6:
            sensor._data = "Brennvorgang beendet"
        elif status == 7:
            sensor._data = "Fehler - Stromversorgung unterbrochen"
        elif status == 8:
            sensor._data = "Fehler"
        else:
            sensor._data = None
        
        return True