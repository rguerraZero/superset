from typing import List


class SupersetRolePermission:
    def __init__(self, permission: str, view_menu: str):
        self._permission: str = permission
        self._view_menu: str = view_menu
        self._errors: List[str] = []

    @property
    def permission(self):
        return self._permission

    @property
    def view_menu(self):
        return self._view_menu

    def _validate(self) -> None:
        """
        validate the permission and view_menu
        """
        if self.permission in [None, ""]:
            self._errors.append("permission is required")

        if self.view_menu in [None, ""]:
            self._errors.append("view_menu is required")

    def is_valid(self) -> bool:
        """
        return True if the permission and view_menu are valid
        """
        return len(self._errors) == 0

    @classmethod
    def from_permission_name(cls, permission_name: str) -> "SupersetRolePermission":
        """
        Create superset permission from permission_name string

        Input example:
            "can read on SavedQuery"

        Transform to:
            SupersetRolePermission("can_read", "SavedQuery")

        """
        permission_name_list = permission_name.split(" on ")
        permission = permission_name_list[0].replace(" ", "_")
        view_menu = permission_name_list[1]

        return cls(permission, view_menu)

    def to_superset_permision_dict(self) -> dict:
        """
        returns a dict that can be used to create a SupersetPermision

        Output example:
            {
                "permission": {
                    "name": "can_this_form_get"
                },
                "view_menu": {
                    "name": "ResetPasswordView"
                }
            },
        """
        return {
            "permission": {"name": self.permission},
            "view_menu": {"name": self.view_menu},
        }
