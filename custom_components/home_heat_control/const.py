from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import (
    UnitOfTemperature,
)

DOMAIN = "home_heat_control"
DEFAULT_NAME = "homeheatcontrol"
DEFAULT_SCAN_INTERVAL = 5
DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDRESS = 0

ATTR_STATUS_DESCRIPTION = "status_description"
ATTR_MANUFACTURER = "M Engineering"
CONF_MODBUS_ADDRESS = "modbus_address"

#attributes: type(0=normal | 1=binary), name, key, unit, class, icon
HHCSENSOR_TYPES = {
    "FBL_SW_Version": [0, "FBL Software Version", "fbl_sw_version", None, None, None],
    "APPL_SW_Version": [0, "APPL Software Version", "appl_sw_version", None, None, None],
    "DTC_Active": [1, "DTCs Aktiv", "dtcactive", None, BinarySensorDeviceClass.PROBLEM, None],
    "Outside_Temperature": [0, "Außentemperatur", "outsidetemperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Room1_Temperature": [0, "Raum 1 Temperatur", "room1temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Room2_Temperature": [0, "Raum 2 Temperatur", "room2temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Doorbell_Status": [0, "Türklingel Status", "doorbell_status", None, None, None],
    "HeatControlManagementEnabled": [1, "Hauptschalter", "heatcontrolmanagement_enabled", None, None, None],
}