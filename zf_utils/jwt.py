import logging
import jwt

from flask import current_app, Request
from typing import Any, Dict

logger = logging.getLogger(__name__)


class JWTParser:

    @classmethod
    def parse_jwt_from_request(cls, req: Request) -> Dict[str, Any]:
        _jwt_secret = current_app.config.get("ZF_JWT_PUBLIC_SECRET")
        token = req.headers.get('Authorization').split(" ")[1]
        if not token:
            raise Exception("Token not present")
        try:
            return jwt.decode(token, _jwt_secret, algorithms=["RS512"])
        except Exception as ex:
            logger.warning("Parse jwt failed", exc_info=True)
            raise Exception("Failed to parse token") from ex