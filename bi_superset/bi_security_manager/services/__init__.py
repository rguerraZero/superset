import pandas as pd


class BQRoleGather:
    def _format_as_superset_role(self, roles: list):
        """
        Format roles as a list of dictionaries
        ---
        Parameters:
            roles: list : list of roles
        Returns:
            roles: list : list of dictionaries
        """

        pass

    def _format_role_access_into_superset_permission(self, role: str) -> dict:
        """
        Split role_access into name and view
        """
        split_role = role.split(" on ")

        permission_dict = {
            "premission": {"name": split_role[0].replace(" ", "_")},
            "view_menu": {"name": split_role[1]},
        }

        return permission_dict

    def get_roles_from_bq(self, superset_access: str, role_name: str) -> pd.DataFrame:
        """
        Get roles from BQ
        ---
        Parameters:
            superset_access: string : could be `internal` or `external`
        Returns:
            roles: list : list of roles
        """
        query = """
            ZSd
        """
