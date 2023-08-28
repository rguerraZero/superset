"""Zerofox API User"""

from bi_superset.bi_security_manager.models.access_method import AccessMethod
from bi_superset.bi_security_manager.models.access_origin import AccessOrigin


class User:
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        is_staff: bool,
        is_active: bool,
        enterprise_id: int,
    ):
        self._id: int = id
        self._username: str = username
        self._email: str = email
        self._first_name: str = first_name
        self._last_name: str = last_name
        self._is_staff: bool = is_staff
        self._is_active: bool = is_active
        self._role_name: str = None
        self._enterprise_id: int = enterprise_id

    @property
    def is_staff(self) -> bool:
        return self._is_staff is True

    @property
    def is_active(self) -> bool:
        return self._is_active is True

    @property
    def email(self) -> str:
        return self._email

    @property
    def username(self) -> str:
        return self._username

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def enterprise_id(self) -> int:
        return self._enterprise_id

    @property
    def access_method(self) -> str:
        if self.is_staff or self.email.endswith("@zerofox.com"):
            return AccessMethod.INTERNAL.value
        return AccessMethod.EXTERNAL.value

    @property
    def is_internal_user(self) -> bool:
        return self.is_staff or self.email.endswith("@zerofox.com")

    @property
    def role_name(self) -> str:
        return self._role_name

    def superset_role_name(self, access_origin) -> str:
        if AccessOrigin.is_from_zf_dashboard(access_origin):
            return f"view_only_{self.enterprise_id}"
        return self.role_name

    @role_name.setter
    def role_name(self, role_name: str):
        self._role_name = role_name

    @classmethod
    def from_dict(cls, i_dict) -> "User":
        return cls(
            id=i_dict.get("id"),
            username=i_dict.get("username"),
            email=i_dict.get("email"),
            first_name=i_dict.get("first_name"),
            last_name=i_dict.get("last_name"),
            is_staff=i_dict.get("is_staff", 0) == 1,
            is_active=i_dict.get("is_active", 0) == 1,
            enterprise_id=i_dict.get("enterprise_id", None),
        )
