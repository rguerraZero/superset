"""
Bigquery sql adapter for sql database
"""
# Libraries
import pandas as pd
import pandas_gbq as gbq
import google.auth

# Abstract class
from bi_security_manager.port.a_sql import ASql


class BigquerySQL(ASql):
    def __init__(self) -> None:
        credentials, _ = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/bigquery",
            ]
        )
        gbq.context.credentials = credentials

    def get_df(self, query: str) -> pd.DataFrame:
        """
        Returns a dataframe from a given query in Bigquery
        """
        if query is None or query == "":
            raise ValueError("query is required")

        try:
            df = gbq.read_gbq(query, project_id="csdataanalysis")
            return df
        except Exception as e:
            raise ValueError(f"Error getting dataframe from bigquery: {e}")

    def get_schema(self, schema_name: str, table_name: str) -> pd.DataFrame:
        """
        Returns a dataframe containing the schema of the table in Bigquery
        """
        if schema_name is None or table_name is None:
            raise ValueError("schema_name and table_name are required")

        query = """
            SELECT
                column_name,
                data_type
            FROM
            `csdataanalysis.{schema}.INFORMATION_SCHEMA.COLUMNS`
            WHERE 1 = 1
            AND table_name='{table_name}'
        """.format(
            schema=schema_name, table_name=table_name
        )

        try:
            df = self.get_df(query=query)
            return df
        except Exception as e:
            raise ValueError(f"Error getting schema from bigquery: {e}")
