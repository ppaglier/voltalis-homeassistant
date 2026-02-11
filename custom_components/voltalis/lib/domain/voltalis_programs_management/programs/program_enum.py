from enum import StrEnum


class ProgramTypeEnum(StrEnum):
    """Enum to represent the type of program"""

    MANUAL = "manual"
    DEFAULT = "default"
    USER = "user"
    QUICK = "quick"
