import logging
from http import HTTPStatus

from flask import Response
from flask_restful import Resource
from redis.exceptions import ConnectionError as RedisConnectionError
from requests.exceptions import ConnectionError

from config.config import DEFAULT_MIMETYPE, redis_db, vault_client

logger = logging.getLogger()


class HealthCheck(Resource):
    def get(self) -> Response:
        try:
            redis_db.ping()
            vault_client.is_initialized()
        except (ConnectionError, RedisConnectionError):
            logger.error("Either redis or vault isn't initialized")
            return Response(
                response="The service is not responsible due to database/vault error",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                mimetype=DEFAULT_MIMETYPE,
            )
        return Response(
            response="The service is up and running",
            status=HTTPStatus.OK,
            mimetype=DEFAULT_MIMETYPE,
        )
