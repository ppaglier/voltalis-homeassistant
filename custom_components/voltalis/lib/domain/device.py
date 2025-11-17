from enum import StrEnum

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisDeviceTypeEnum(StrEnum):
    """Enum for the type field"""

    HEATER = "HEATER"
    WATER_HEATER = "WATER_HEATER"


class VoltalisDeviceModulatorTypeEnum(StrEnum):
    """Enum for the modulator_type field"""

    VX_WIRE = "VX_WIRE"
    VX_RELAY = "VX_RELAY"


class VoltalisDeviceModeEnum(StrEnum):
    """Enum for the available_modes field"""

    ECO = "ECO"
    CONFORT = "CONFORT"
    TEMPERATURE = "TEMPERATURE"
    HORS_GEL = "HORS_GEL"
    NORMAL = "NORMAL"
    ECOV = "ECOV"


class VoltalisDeviceProgTypeEnum(StrEnum):
    """Enum for the type field"""

    MANUAL = "MANUAL"
    DEFAULT = "DEFAULT"
    USER = "USER"


class VoltalisDevice(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str
    type: VoltalisDeviceTypeEnum
    modulator_type: VoltalisDeviceModulatorTypeEnum
    available_modes: list[VoltalisDeviceModeEnum]
    prog_type: VoltalisDeviceProgTypeEnum


class VoltalisConsumptionObjective(CustomModel):
    """Class to represent consumption objectives"""

    yearly_objective_in_wh: float
    yearly_objective_in_currency: float


class VoltalisRealTimeConsumption(CustomModel):
    """Class to represent a single real-time consumption data point"""

    timestamp: str
    total_consumption_in_wh: float
    total_consumption_in_currency: float


class VoltalisProgram(CustomModel):
    """Class to represent a Voltalis program"""

    id: int
    name: str
    enabled: bool
    program_type: VoltalisDeviceProgTypeEnum
    program_name: str
    until_further_notice: bool
    end_date: str | None
    geoloc_currently_on: bool


class VoltalisContractPeakHours(CustomModel):
    """Class to represent peak/off-peak hours"""

    from_time: str  # "HH:MM"
    to_time: str  # "HH:MM"


class VoltalisContract(CustomModel):
    """Class to represent subscriber contract information"""

    id: int
    name: str
    is_default: bool
    subscribed_power: int  # in kVA or kW
    is_peak_off_peak_contract: bool
    subscription_base_price: float | None
    subscription_peak_and_off_peak_hour_base_price: float
    kwh_base_price: float | None
    kwh_peak_hour_price: float
    kwh_offpeak_hour_price: float
    company_name: str
    peak_hours: list[VoltalisContractPeakHours]
    offpeak_hours: list[VoltalisContractPeakHours]


class VoltalisSiteInfo(CustomModel):
    """Class to represent site information"""

    id: int
    address: str
    name: str
    postal_code: str
    city: str
    country: str
    timezone: str
    voltalis_version: str
    installation_date: str
    has_global_consumption_measure: bool
    has_dso_measure: bool


class VoltalisApplianceProgramming(CustomModel):
    """Class to represent appliance programming state"""

    prog_type: VoltalisDeviceProgTypeEnum
    prog_name: str | None
    id_manual_setting: int | None
    is_on: bool
    until_further_notice: bool | None
    mode: VoltalisDeviceModeEnum
    id_planning: int | None
    end_date: str | None
    temperature_target: float | None
    default_temperature: float


class VoltalisManagedAppliance(CustomModel):
    """Class to represent a managed appliance with full details"""

    id: int
    name: str
    type: VoltalisDeviceTypeEnum
    modulator_type: VoltalisDeviceModulatorTypeEnum
    available_modes: list[VoltalisDeviceModeEnum]
    voltalis_version: str
    programming: VoltalisApplianceProgramming
    heating_level: int  # 0-100


class VoltalisDiagnosticStatusEnum(StrEnum):
    """Enum for diagnostic status"""

    OK = "OK"
    NO_CONSUMPTION = "NO_CONSUMPTION"


class VoltalisApplianceDiagnostic(CustomModel):
    """Class to represent appliance diagnostic information"""

    name: str
    cs_modulator_id: int
    cs_appliance_id: int
    status: VoltalisDiagnosticStatusEnum
    diag_test_enabled: bool
