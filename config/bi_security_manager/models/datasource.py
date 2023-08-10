class DataSource:
    def __init__(self, database: str, project: str, schema: str, table: str):
        self._database = database
        self._project = project
        self._schema = schema
        self._table = table

    def is_valid(self) -> bool:
        if self.database in [None, ""]:
            return False

    @property
    def database(self):
        return self._database + "/" + self._project

    @property
    def schema(self):
        return self._schema

    @property
    def table(self):
        return self._table

    @classmethod
    def from_dict(cls, i_dict: dict) -> "DataSource":
        return cls(
            database=i_dict.get("database"),
            project=i_dict.get("table_catalog"),
            schema=i_dict.get("table_schema"),
            table=i_dict.get("table_name"),
        )
