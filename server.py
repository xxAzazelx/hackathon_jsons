from flask import Flask
from flask_restful import Api

from blueprints.get_data import GetData
from blueprints.healthcheck import HealthCheck
from blueprints.upload_json import JSONUpload


def create_api():
    application = Flask("json_parser")
    api = Api(application)

    api.add_resource(HealthCheck, "/")
    api.add_resource(GetData, "/vm_data/")
    api.add_resource(JSONUpload, "/update_json/")

    return application
