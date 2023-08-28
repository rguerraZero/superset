# enum for access origin
from enum import Enum


class AccessOrigin(Enum):
    SUPERSET_UI = "superset_ui"
    ZF_DASHBOARD = "zf_dashboard"

    @classmethod
    def is_from_superset_ui(cls, value) -> bool:
        return cls.SUPERSET_UI.value == value

    @classmethod
    def is_from_zf_dashboard(cls, value) -> bool:
        return cls.ZF_DASHBOARD.value == value
