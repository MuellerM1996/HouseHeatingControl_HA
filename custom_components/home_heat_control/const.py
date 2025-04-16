from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntityDescription
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE
)

DOMAIN = "home_heat_control"
DEFAULT_NAME = "homeheatcontrol"
DEFAULT_SCAN_INTERVAL = 5
DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDRESS = 0

ATTR_MANUFACTURER = "MM/HL Engineering"
CONF_MODBUS_ADDRESS = "modbus_address"

#attributes: type(0=normal | 1=binary), name, key is mandatory
HHCSENSOR_TYPES = [
    #General
    [DEFAULT_MODBUS_ADDRESS, 0, SensorEntityDescription(name="FBL Software Version", key="fbl_sw_version")],
    [DEFAULT_MODBUS_ADDRESS, 1, SensorEntityDescription(name="APPL Software Version", key="appl_sw_version")],
    [DEFAULT_MODBUS_ADDRESS, 3, BinarySensorEntityDescription(name="DTCs Aktiv", key="dtcactive", device_class=BinarySensorDeviceClass.PROBLEM)],
    #General Temperatures
    [DEFAULT_MODBUS_ADDRESS, 20, SensorEntityDescription(name="Außentemperatur", key="outsidetemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 21, SensorEntityDescription(name="Raum 1 Temperatur", key="room1temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 22, SensorEntityDescription(name="Raum 2 Temperatur", key="room2temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #Doorbell
    [DEFAULT_MODBUS_ADDRESS, 25, SensorEntityDescription(name="Türklingel Status" , key="doorbell_status", device_class=SensorDeviceClass.ENUM, icon="mdi:bell")],
    #Heat control management
    [DEFAULT_MODBUS_ADDRESS, 30, SwitchEntityDescription(name="Hauptschalter", key="heatcontrolmanagement_enabled", device_class=SwitchDeviceClass.SWITCH)],
    [DEFAULT_MODBUS_ADDRESS, 31, BinarySensorEntityDescription(name="Temperatur niedrig Warnung", key="heatcontrolmanagement_lowTemperatureWarning", device_class=BinarySensorDeviceClass.COLD)],
    #HC1
    [DEFAULT_MODBUS_ADDRESS, 40, SensorEntityDescription(name="HK1 Status" , key="heatcircuit_1_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 41, SensorEntityDescription(name="HK1 Pumpenstatus" , key="heatcircuit_1_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 42, SensorEntityDescription(name="HK1 Mischerstatus" , key="heatcircuit_1_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 43, BinarySensorEntityDescription(name="HK1 Mischer normiert", key="heatcircuit_1_mixernormed")],
    [DEFAULT_MODBUS_ADDRESS, 44, SensorEntityDescription(name="HK1 Mischer Position", key="heatcircuit_1_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 45, SensorEntityDescription(name="HK1 Zielvorlauftemperatur", key="heatcircuit_1_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 46, SensorEntityDescription(name="HK1 Vorlauftemperatur", key="heatcircuit_1_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 47, SensorEntityDescription(name="HK1 Rücklauftemperatur", key="heatcircuit_1_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #HC2
    [DEFAULT_MODBUS_ADDRESS, 60, SensorEntityDescription(name="HK2 Status" , key="heatcircuit_2_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 61, SensorEntityDescription(name="HK2 Pumpenstatus" , key="heatcircuit_2_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 62, SensorEntityDescription(name="HK2 Mischerstatus" , key="heatcircuit_2_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 63, BinarySensorEntityDescription(name="HK2 Mischer normiert", key="heatcircuit_2_mixernormed")],
    [DEFAULT_MODBUS_ADDRESS, 64, SensorEntityDescription(name="HK2 Mischer Position", key="heatcircuit_2_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 65, SensorEntityDescription(name="HK2 Zielvorlauftemperatur", key="heatcircuit_2_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 66, SensorEntityDescription(name="HK2 Vorlauftemperatur", key="heatcircuit_2_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 67, SensorEntityDescription(name="HK2 Rücklauftemperatur", key="heatcircuit_2_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #HC3
    [DEFAULT_MODBUS_ADDRESS, 80, SensorEntityDescription(name="HK3 Status" , key="heatcircuit_3_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 81, SensorEntityDescription(name="HK3 Pumpenstatus" , key="heatcircuit_3_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 82, SensorEntityDescription(name="HK3 Mischerstatus" , key="heatcircuit_3_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 83, BinarySensorEntityDescription(name="HK3 Mischer normiert", key="heatcircuit_3_mixernormed")],
    [DEFAULT_MODBUS_ADDRESS, 84, SensorEntityDescription(name="HK3 Mischer Position", key="heatcircuit_3_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 85, SensorEntityDescription(name="HK3 Zielvorlauftemperatur", key="heatcircuit_3_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 86, SensorEntityDescription(name="HK3 Vorlauftemperatur", key="heatcircuit_3_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 87, SensorEntityDescription(name="HK3 Rücklauftemperatur", key="heatcircuit_3_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #Bufferstorage
    [DEFAULT_MODBUS_ADDRESS, 100, SensorEntityDescription(name="Pufferspeicher Status" , key="bufferstorage_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 101, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Oben", key="bufferstorage_1_temperature_top", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 102, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Mitte-Oben", key="bufferstorage_1_temperature_middletop", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 103, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Mitte-Unten", key="bufferstorage_1_temperature_middlebottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 104, SensorEntityDescription(name="Pufferspeicher 1 Temperatur Unten", key="bufferstorage_1_temperature_bottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 105, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Oben", key="bufferstorage_2_temperature_top", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 106, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Mitte-Oben", key="bufferstorage_2_temperature_middletop", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 107, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Mitte-Unten", key="bufferstorage_2_temperature_middlebottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 108, SensorEntityDescription(name="Pufferspeicher 2 Temperatur Unten", key="bufferstorage_2_temperature_bottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 109, SensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer Status" , key="bufferstorage_charge_or_switch_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 110, BinarySensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer normiert", key="bufferstorage_charge_or_switch_mixernormed")],
    [DEFAULT_MODBUS_ADDRESS, 111, SensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer Position", key="bufferstorage_charge_or_switch_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 112, SensorEntityDescription(name="Pufferspeicher Ladepumpenstatus" , key="bufferstorage_chargepumpstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 113, SensorEntityDescription(name="Pufferspeicher Ladewassertemperatur", key="bufferstorage_chargewatertemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 114, SensorEntityDescription(name="Pufferspeicher 1 Füllstand", key="bufferstorage_1_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 115, SensorEntityDescription(name="Pufferspeicher 2 Füllstand", key="bufferstorage_2_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 116, SensorEntityDescription(name="Pufferspeicher kombinierter Füllstand", key="bufferstorage_combined_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [DEFAULT_MODBUS_ADDRESS, 117, SensorEntityDescription(name="Pufferspeicher Aktiv Status" , key="bufferstorage_active_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 118, SensorEntityDescription(name="Pufferspeicher Ladeventilventilstatus" , key="bufferstorage_chargevalvestatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 119, SensorEntityDescription(name="Pufferspeicher Ladestatus" , key="bufferstorage_chargestatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 120, BinarySensorEntityDescription(name="Pufferspeicher nur E-Laden", key="bufferstorage_chargeElectricOnly")],
    #WarmWater
    [DEFAULT_MODBUS_ADDRESS, 140, SensorEntityDescription(name="Warmwasser Boiler Status" , key="warmwater_boiler_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 141, SensorEntityDescription(name="Warmwasser Boiler Temperatur", key="warmwater_boiler_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 142, SensorEntityDescription(name="Warmwasser Boiler Ladepumpenstatus" , key="warmwater_boiler_chargepumpstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 143, SensorEntityDescription(name="Warmwasser Boiler Umschaltventilstatus" , key="warmwater_boiler_valvestatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 144, BinarySensorEntityDescription(name="Warmwasser Boiler manuelles laden", key="warmwater_boiler_manualChargeActive")],
    [DEFAULT_MODBUS_ADDRESS, 147, BinarySensorEntityDescription(name="Warmwasser Bad heizen aktiv", key="warmwater_bath_heatingactive")],
    [DEFAULT_MODBUS_ADDRESS, 150, SensorEntityDescription(name="Warmwasser Zirkulation Abgabetemperatur", key="warmwater_circulation_outputtemerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 151, SensorEntityDescription(name="Warmwasser Zirkulation Pumpenstatus" , key="warmwater_circulation_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 152, SensorEntityDescription(name="Warmwasser Zirkulation Kreis 1 Status" , key="warmwater_circulation_circuit1_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 153, SensorEntityDescription(name="Warmwasser Zirkulation Kreis 1 Temperatur", key="warmwater_circulation_circuit1_temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 154, SensorEntityDescription(name="Warmwasser Zirkulation Kreis 1 Ventilstatus" , key="warmwater_circulation_circuit1_valvestatus", device_class=SensorDeviceClass.ENUM)],
    #TODO:
    [DEFAULT_MODBUS_ADDRESS, 156, SensorEntityDescription(name="Warmwasser Zirkulation Kreis 2 Status" , key="warmwater_circulation_circuit2_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 157, SensorEntityDescription(name="Warmwasser Zirkulation Kreis 2 Temperatur", key="warmwater_circulation_circuit2_temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 158, SensorEntityDescription(name="Warmwasser Zirkulation Kreis 2 Ventilstatus" , key="warmwater_circulation_circuit2_valvestatus", device_class=SensorDeviceClass.ENUM)],
    #TODO:
    #Woodburner
    [DEFAULT_MODBUS_ADDRESS, 170, SensorEntityDescription(name="Holzofen Status" , key="woodburner_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 171, SensorEntityDescription(name="Holzofen Abgastemperatur", key="woodburner_exhaust_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 172, SensorEntityDescription(name="Holzofen Wassertemperatur", key="woodburner_water_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #Gasburner
    [DEFAULT_MODBUS_ADDRESS, 180, SensorEntityDescription(name="Gasbrenner Status" , key="gasburner_status", device_class=SensorDeviceClass.ENUM)],
    [DEFAULT_MODBUS_ADDRESS, 181, SensorEntityDescription(name="Gasbrenner Abgastemperatur", key="gasburner_exhaust_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [DEFAULT_MODBUS_ADDRESS, 182, SensorEntityDescription(name="Gasbrenner Wassertemperatur", key="gasburner_water_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
]