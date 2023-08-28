"""SQL Alchemy Models implementation of BI Tables"""

from flask_appbuilder import Model
from sqlalchemy import Boolean, Column, String, Integer, Sequence


class RolesPerJobTitle(Model):
    __tablename__ = "bi_roles_per_job_title"

    username = Column(String(256), primary_key=True)
    role_name = Column(String(256))

    def __repr__(self):
        return self.username

    @classmethod
    def from_dict(cls, i_dict) -> "RolesPerJobTitle":
        return cls(
            username=i_dict.get("employee"),
            role_name=i_dict.get("role_name").lower().replace(" ", "_"),
        )

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "role_name": self.role_name,
        }


class DataSourceAccess(Model):
    __tablename__ = "bi_datasource_access"
    id = Column(Integer, Sequence("datasource_access_id_seq"), primary_key=True)
    database = Column(String(256))
    table_catalog = Column(String(256))
    table_schema = Column(String(256))
    table_name = Column(String(256))
    role_name = Column(String(256))

    @classmethod
    def from_dict(cls, i_dict: dict, role_name: str) -> "DataSourceAccess":
        return cls(
            database=i_dict.get("database"),
            table_catalog=i_dict.get("table_catalog"),
            table_schema=i_dict.get("table_schema"),
            table_name=i_dict.get("table_name"),
            role_name=role_name,
        )

    def to_dict(self) -> dict:
        return {
            "database": self.database,
            "table_catalog": self.table_catalog,
            "table_schema": self.table_schema,
            "table_name": self.table_name,
            "role_name": self.role_name,
        }


class DashboardRoleAccessExternal(Model):
    __tablename__ = "bi_dashboard_role_access_external"

    id = Column(Integer, Sequence("dashboard_role_access_id_seq"), primary_key=True)
    dashboard_id = Column(Integer)
    role_name = Column(String(256))

    @classmethod
    def from_dict(cls, row):
        return cls(
            role_name=row["role_name"],
            dashboard_id=row["dashboard_id"],
        )

    def to_dict(self):
        return {
            "role_name": self.role_name,
            "dashboard_id": self.dashboard_id,
        }
