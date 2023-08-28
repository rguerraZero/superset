# enum for access methods
from enum import Enum


class AccessMethod(Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

    @classmethod
    def is_external(cls, value) -> bool:
        return cls.EXTERNAL.value == value
    
    @classmethod
    def is_internal(cls, value) -> bool:
        return cls.INTERNAL.value == value
