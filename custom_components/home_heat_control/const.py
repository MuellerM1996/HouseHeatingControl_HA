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
#    "DTC_Active": [1, "Master DTCs Active", "dtcactive", None, BinarySensorDeviceClass.PROBLEM, None],
    "Outside_Temperature": [0, "Außentemperatur", "outsidetemperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
}