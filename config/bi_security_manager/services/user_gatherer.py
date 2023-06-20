from bi_security_manager.port.a_sql import ASql
from bi_security_manager.models.user import User
from bi_security_manager.sql.queries import (
    CACHE_USER_DATA_QUERY,
)


class UserGatherer:
    """Gather a specific user from zf api cache. located in Bigquery"""

    def __init__(self, sql: ASql):
        self.sql = sql

    def get_user(self, user_email: str) -> User:
        """
        Returns user from zf api cache
        """
        if user_email is None:
            raise ValueError("user_email is required")

        query = CACHE_USER_DATA_QUERY.format(email=user_email)

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError("user not found")

        if df.shape[0] > 1:
            raise ValueError("user found more than once")

        return User.from_dict(df.to_dict(orient="records")[0])
