from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntityDescription
from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import (
    UnitOfTemperature
)
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass

DOMAIN = "home_heat_control"
DEFAULT_NAME = "homeheatcontrol"
DEFAULT_SCAN_INTERVAL = 5
DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDRESS = 0

ATTR_STATUS_DESCRIPTION = "status_description"
ATTR_MANUFACTURER = "MM/HL Engineering"
CONF_MODBUS_ADDRESS = "modbus_address"

#attributes: type(0=normal | 1=binary), name, key is mandatory
HHCSENSOR_TYPES = [
    [0, SensorEntityDescription(name="FBL Software Version", key="fbl_sw_version")],
    [0, SensorEntityDescription(name="APPL Software Version", key="appl_sw_version")],
    [1, BinarySensorEntityDescription(name="DTCs Aktiv", key="dtcactive", device_class=BinarySensorDeviceClass.PROBLEM)],
    [0, SensorEntityDescription(name="Außentemperatur", key="outsidetemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Raum 1 Temperatur", key="room1temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Raum 2 Temperatur", key="room2temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Türklingel Status" , key="doorbell_status", device_class=SensorDeviceClass.ENUM, icon="mdi:bell")],
    [1, BinarySensorEntityDescription(name="Hauptschalter", key="heatcontrolmanagement_enabled")],
]