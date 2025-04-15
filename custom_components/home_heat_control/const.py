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
    [SensorEntityDescription(name="FBL Software Version", key="fbl_sw_version")],
    [SensorEntityDescription(name="APPL Software Version", key="appl_sw_version")],
    [BinarySensorEntityDescription(name="DTCs Aktiv", key="dtcactive", device_class=BinarySensorDeviceClass.PROBLEM)],
    #General Temperatures
    [SensorEntityDescription(name="Außentemperatur", key="outsidetemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Raum 1 Temperatur", key="room1temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Raum 2 Temperatur", key="room2temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #Doorbell
    [SensorEntityDescription(name="Türklingel Status" , key="doorbell_status", device_class=SensorDeviceClass.ENUM, icon="mdi:bell")],
    #Heat control management
    [SwitchEntityDescription(name="Hauptschalter", key="heatcontrolmanagement_enabled", device_class=SwitchDeviceClass.SWITCH), DEFAULT_MODBUS_ADDRESS, 30],
    [BinarySensorEntityDescription(name="Temperatur niedrig Warnung", key="heatcontrolmanagement_lowTemperatureWarning", device_class=BinarySensorDeviceClass.COLD)],
    #HC1
    [SensorEntityDescription(name="HK1 Status" , key="heatcircuit_1_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="HK1 Pumpenstatus" , key="heatcircuit_1_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="HK1 Mischerstatus" , key="heatcircuit_1_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [BinarySensorEntityDescription(name="HK1 Mischer normiert", key="heatcircuit_1_mixernormed")],
    [SensorEntityDescription(name="HK1 Mischer Position", key="heatcircuit_1_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="HK1 Zielvorlauftemperatur", key="heatcircuit_1_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="HK1 Vorlauftemperatur", key="heatcircuit_1_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="HK1 Rücklauftemperatur", key="heatcircuit_1_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #HC2
    [SensorEntityDescription(name="HK2 Status" , key="heatcircuit_2_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="HK2 Pumpenstatus" , key="heatcircuit_2_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="HK2 Mischerstatus" , key="heatcircuit_2_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [BinarySensorEntityDescription(name="HK2 Mischer normiert", key="heatcircuit_2_mixernormed")],
    [SensorEntityDescription(name="HK2 Mischer Position", key="heatcircuit_2_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="HK2 Zielvorlauftemperatur", key="heatcircuit_2_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="HK2 Vorlauftemperatur", key="heatcircuit_2_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="HK2 Rücklauftemperatur", key="heatcircuit_2_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #HC3
    [SensorEntityDescription(name="HK3 Status" , key="heatcircuit_3_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="HK3 Pumpenstatus" , key="heatcircuit_3_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="HK3 Mischerstatus" , key="heatcircuit_3_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [BinarySensorEntityDescription(name="HK3 Mischer normiert", key="heatcircuit_3_mixernormed")],
    [SensorEntityDescription(name="HK3 Mischer Position", key="heatcircuit_3_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="HK3 Zielvorlauftemperatur", key="heatcircuit_3_targetForerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="HK3 Vorlauftemperatur", key="heatcircuit_3_forerunTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="HK3 Rücklauftemperatur", key="heatcircuit_3_returnflowTemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #TODO: Timer + Settings
    #Bufferstorage
    [SensorEntityDescription(name="Pufferspeicher Status" , key="bufferstorage_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Pufferspeicher 1 Temperatur Oben", key="bufferstorage_1_temperature_top", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 1 Temperatur Mitte-Oben", key="bufferstorage_1_temperature_middletop", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 1 Temperatur Mitte-Unten", key="bufferstorage_1_temperature_middlebottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 1 Temperatur Unten", key="bufferstorage_1_temperature_bottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 2 Temperatur Oben", key="bufferstorage_2_temperature_top", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 2 Temperatur Mitte-Oben", key="bufferstorage_2_temperature_middletop", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 2 Temperatur Mitte-Unten", key="bufferstorage_2_temperature_middlebottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 2 Temperatur Unten", key="bufferstorage_2_temperature_bottom", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer Status" , key="bufferstorage_charge_or_switch_mixerstatus", device_class=SensorDeviceClass.ENUM)],
    [BinarySensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer normiert", key="bufferstorage_charge_or_switch_mixernormed")],
    [SensorEntityDescription(name="Pufferspeicher Lade/Umschalt Mischer Position", key="bufferstorage_charge_or_switch_mixerposition", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="Pufferspeicher Ladepumpenstatus" , key="bufferstorage_chargepumpstatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Pufferspeicher Ladewassertemperatur", key="bufferstorage_chargewatertemperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Pufferspeicher 1 Füllstand", key="bufferstorage_1_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="Pufferspeicher 2 Füllstand", key="bufferstorage_2_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="Pufferspeicher kombinierter Füllstand", key="bufferstorage_combined_filllevel", state_class=SensorStateClass.MEASUREMENT, unit_of_measurement=PERCENTAGE)],
    [SensorEntityDescription(name="Pufferspeicher Aktiv Status" , key="bufferstorage_active_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Pufferspeicher Ladeventilventilstatus" , key="bufferstorage_chargevalvestatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Pufferspeicher Ladestatus" , key="bufferstorage_chargestatus", device_class=SensorDeviceClass.ENUM)],
    [BinarySensorEntityDescription(name="Pufferspeicher nur E-Laden", key="bufferstorage_chargeElectricOnly")],
    #WarmWater
    [SensorEntityDescription(name="Warmwasser Boiler Status" , key="warmwater_boiler_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Warmwasser Boiler Temperatur", key="warmwater_boiler_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Warmwasser Boiler Ladepumpenstatus" , key="warmwater_boiler_chargepumpstatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Warmwasser Boiler Umschaltventilstatus" , key="warmwater_boiler_valvestatus", device_class=SensorDeviceClass.ENUM)],
    [BinarySensorEntityDescription(name="Warmwasser Boiler manuelles laden", key="warmwater_boiler_manualChargeActive")],
    [BinarySensorEntityDescription(name="Warmwasser Bad heizen aktiv", key="warmwater_bath_heatingactive")],
    [SensorEntityDescription(name="Warmwasser Zirkulation Abgabetemperatur", key="warmwater_circulation_outputtemerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Pumpenstatus" , key="warmwater_circulation_pumpstatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Kreis 1 Status" , key="warmwater_circulation_circuit1_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Kreis 1 Temperatur", key="warmwater_circulation_circuit1_temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Kreis 1 Ventilstatus" , key="warmwater_circulation_circuit1_valvestatus", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Kreis 2 Status" , key="warmwater_circulation_circuit2_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Kreis 2 Temperatur", key="warmwater_circulation_circuit2_temperature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Warmwasser Zirkulation Kreis 2 Ventilstatus" , key="warmwater_circulation_circuit2_valvestatus", device_class=SensorDeviceClass.ENUM)],
    #Woodburner
    [SensorEntityDescription(name="Holzofen Status" , key="woodburner_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Holzofen Abgastemperatur", key="woodburner_exhaust_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Holzofen Wassertemperatur", key="woodburner_water_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    #Gasburner
    [SensorEntityDescription(name="Gasbrenner Status" , key="gasburner_status", device_class=SensorDeviceClass.ENUM)],
    [SensorEntityDescription(name="Gasbrenner Abgastemperatur", key="gasburner_exhaust_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
    [SensorEntityDescription(name="Gasbrenner Wassertemperatur", key="gasburner_water_temerature", state_class=SensorStateClass.MEASUREMENT, device_class=SensorDeviceClass.TEMPERATURE, unit_of_measurement=UnitOfTemperature.CELSIUS)],
]