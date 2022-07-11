from datetime import datetime
from http import HTTPStatus
from string import Template
from typing import Optional

from cryptography.fernet import Fernet
from flask import Response, request
from flask_restful import Resource

from config.config import DEFAULT_MIMETYPE, redis_db, vault_client


class GetData(Resource):
    def get(self) -> Response:
        vm_id = request.args.get("vm_index")
        vault_key = request.args.get("vault_key")

        if not vm_id:
            return Response(
                response="The request didn't contain the required parameter <vm_index>",
                status=HTTPStatus.BAD_REQUEST,
                mimetype=DEFAULT_MIMETYPE,
            )

        non_parsed_data = redis_db.hgetall(vm_id)
        if not non_parsed_data:
            return Response(
                response=f"There's no data concerning virtual machine {vm_id}",
                status=HTTPStatus.OK,
                mimetype=DEFAULT_MIMETYPE,
            )

        parsed_data = {key.decode(): value.decode() for key, value in non_parsed_data.items()}
        response = self.__create_response_template(vm_id=vm_id, redis_data=parsed_data, vault_key=vault_key)
        if parsed_data.get("isMeta"):
            response += self.__create_meta_template(redis_data=parsed_data)

        return Response(
            response=response,
            status=HTTPStatus.OK,
            mimetype=DEFAULT_MIMETYPE,
        )

    def __create_response_template(self, vm_id: str, redis_data: dict, vault_key: Optional[bytes] = None):
        template_string = """
        The virtual machine $vm_id can be found under IP $host.
        Username and password required to login are: $username [$password].
        The interfaces that are available are: $interfaces.
        """
        username = redis_data.get("username")
        password = redis_data.get("password")

        """This needs to be changed I didn't have time to setup it"""
        if vault_key:
            vault_client.token = vault_key
            key = vault_client.secrets.kv.read_secret_version(path="secrets")["data"]["data"]["decryption_key"]
            cipher = Fernet(key.encode())
            username = cipher.decrypt(username.encode()).decode()
            password = cipher.decrypt(password.encode()).decode()
            vault_client.token = ""

        template_obj = Template(template_string)
        return template_obj.substitute(
            vm_id=vm_id,
            host=redis_data.get("host"),
            username=username,
            password=password,
            interfaces=redis_data.get("interfaces"),
        )

    def __create_meta_template(self, redis_data: dict) -> str:
        template_string = """
        UUID: $uuid,
        Created at: $creation with lease ending at $expiration,
        Managed by $owner.
        """

        template_obj = Template(template_string)
        return template_obj.substitute(
            uuid=redis_data.get("uuid"),
            creation=self.__to_date(int(redis_data.get("createdAt"))),
            expiration=self.__to_date(int(redis_data.get("expirationDate"))),
            owner=redis_data.get("team"),
        )

    @staticmethod
    def __to_date(timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp)
