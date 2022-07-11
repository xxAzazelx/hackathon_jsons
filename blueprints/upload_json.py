import logging
from http import HTTPStatus
from json import dumps
from os import remove as remove_file
from os.path import join

import ijson
from flask import Response, request
from flask_restful import Resource

from config.config import DEFAULT_MIMETYPE, DataParams, redis_db

logger = logging.getLogger()


class JSONUpload(Resource):
    def post(self) -> Response:
        file = request.files.get("vm_data")
        if not file:
            return Response(
                response="The correct file wasn't provided",
                status=HTTPStatus.BAD_REQUEST,
                mimetype=DEFAULT_MIMETYPE,
            )

        temporary_file = join(DataParams.temp_file_directory, file.filename)
        file.save(temporary_file)

        with open(temporary_file) as json_file:
            for vm, parameters in ijson.kvitems(json_file, prefix=""):
                if DataParams.required_service not in parameters["services"]:
                    continue
                for item, value in parameters.items():
                    self.__common_hset(vm, item, value)
                    if item == "meta":
                        self.__meta_hset(vm, value)
        remove_file(temporary_file)

        return Response(
            response="The file has been uploaded to the DB correctly",
            status=HTTPStatus.CREATED,
            mimetype=DEFAULT_MIMETYPE,
        )

    def __common_hset(self, vm: str, item, value) -> None:
        if item in DataParams.list_params:
            redis_db.hset(name=vm, key=item, value=dumps(value))
        if item in DataParams.common_params:
            redis_db.hset(name=vm, key=item, value=value)

    def __meta_hset(self, vm: str, meta_dict) -> None:
        redis_db.hset(name=vm, key="isMeta", value="True")
        for key, value in meta_dict.items():
            if key in DataParams.meta_params:
                redis_db.hset(name=vm, key=key, value=value)
