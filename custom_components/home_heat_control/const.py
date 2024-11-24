from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntityDescription
from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE
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
    #Genral
    [0, SensorEntityDescription(name="FBL Software Version", key="fbl_sw_version")],
    [0, SensorEntityDescription(name="APPL Software Version", key="appl_sw_version")],
    [1, BinarySensorEntityDescription(name="DTCs Aktiv", key="dtcactive", device_class=BinarySensorDeviceClass.PROBLEM)],
    #General Temperatures
    [0, SensorEntityDescription(name="Außentemperatur", key="outsidetemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Raum 1 Temperatur", key="room1temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Raum 2 Temperatur", key="room2temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #Doorbell
    [0, SensorEntityDescription(name="Türklingel Status" , key="doorbell_status", device_class=SensorDeviceClass.ENUM, icon="mdi:bell")],
    #Heat control management
    [1, BinarySensorEntityDescription(name="Hauptschalter", key="heatcontrolmanagement_enabled")],
    [1, BinarySensorEntityDescription(name="Temperatur niedrig Warnung", key="heatcontrolmanagement_lowTemperatureWarning", device_class=BinarySensorDeviceClass.COLD)],
    #HC1
    [0, SensorEntityDescription(name="HK1 Status" , key="heatcircuit_1_status", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="HK1 Pumpenstatus" , key="heatcircuit_1_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="HK1 Mischerstatus" , key="heatcircuit_1_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [1, BinarySensorEntityDescription(name="HK1 Mischer normiert", key="heatcircuit_1_mixernormed")],
    [0, SensorEntityDescription(name="HK1 Mischer Position", key="heatcircuit_1_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="HK1 Zielvorlauftemperatur", key="heatcircuit_1_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="HK1 Vorlauftemperatur", key="heatcircuit_1_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="HK1 Rücklauftemperatur", key="heatcircuit_1_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #HC2
    [0, SensorEntityDescription(name="HK2 Status" , key="heatcircuit_2_status", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="HK2 Pumpenstatus" , key="heatcircuit_2_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="HK2 Mischerstatus" , key="heatcircuit_2_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [1, BinarySensorEntityDescription(name="HK2 Mischer normiert", key="heatcircuit_2_mixernormed")],
    [0, SensorEntityDescription(name="HK2 Mischer Position", key="heatcircuit_2_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="HK2 Zielvorlauftemperatur", key="heatcircuit_2_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="HK2 Vorlauftemperatur", key="heatcircuit_2_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="HK2 Rücklauftemperatur", key="heatcircuit_2_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #HC3
    [0, SensorEntityDescription(name="HK3 Status" , key="heatcircuit_3_status", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="HK3 Pumpenstatus" , key="heatcircuit_3_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="HK3 Mischerstatus" , key="heatcircuit_3_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [1, BinarySensorEntityDescription(name="HK3 Mischer normiert", key="heatcircuit_3_mixernormed")],
    [0, SensorEntityDescription(name="HK3 Mischer Position", key="heatcircuit_3_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="HK3 Zielvorlauftemperatur", key="heatcircuit_3_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="HK3 Vorlauftemperatur", key="heatcircuit_3_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="HK3 Rücklauftemperatur", key="heatcircuit_3_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #Bufferstorage
    [0, SensorEntityDescription(name="Pufferspeicher Status" , key="bufferstorage_status", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Oben", key="bufferstorage_1_temperature_top", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Mitte-Oben", key="bufferstorage_1_temperature_middletop", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Mitte-Unten", key="bufferstorage_1_temperature_middlebottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Unten", key="bufferstorage_1_temperature_bottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Oben", key="bufferstorage_2_temperature_top", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Mitte-Oben", key="bufferstorage_2_temperature_middletop", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Mitte-Unten", key="bufferstorage_2_temperature_middlebottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Unten", key="bufferstorage_2_temperature_bottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer Status" , key="bufferstorage_charge_or_switch_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [1, BinarySensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer normiert", key="bufferstorage_charge_or_switch_mixernormed")],
    [0, SensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer Position", key="bufferstorage_charge_or_switch_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="Pufferspeicher Ladepumpenstatus" , key="bufferstorage_chargepumpstatus", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="Pufferspeicher Ladewassertemperatur", key="bufferstorage_chargewatertemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Pufferspeicher 1 Füllstand", key="bufferstorage_1_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="Pufferspeicher 2 Füllstand", key="bufferstorage_2_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="Pufferspeicher kombinierter Füllstand", key="bufferstorage_combined_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [0, SensorEntityDescription(name="Pufferspeicher Aktiv Status" , key="bufferstorage_active_status", device_class=SensorDeviceClass.ENUM)],
    #WarmWater
    [0, SensorEntityDescription(name="Warmwasser Boiler Status" , key="warmwater_boiler_status", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="Warmwasser Boiler Temperatur", key="warmwater_boiler_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Warmwasser Boiler Ladepumpenstatus" , key="warmwater_boiler_chargepumpstatus", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="Warmwasser Boiler Umschaltventilstatus" , key="warmwater_boiler_valvestatus", device_class=SensorDeviceClass.ENUM)],
    [1, BinarySensorEntityDescription(name="Warmwasser Bad heizen aktiv", key="warmwater_bath_heatingactive")],
    #Woodburner
    [0, SensorEntityDescription(name="Holzofen Status" , key="woodburner_status", device_class=SensorDeviceClass.ENUM)],
    [0, SensorEntityDescription(name="Holzofen Abgastemperatur", key="woodburner_exhaust_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [0, SensorEntityDescription(name="Holzofen Wassertemperatur", key="woodburner_water_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
]