import logging
from configparser import ConfigParser
from dataclasses import dataclass
from os.path import dirname, join
from typing import List

from hvac import Client as VaultClient
from redis import Redis

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, filename="hackathon_json.log")

try:
    from fakeredis import FakeRedis  # noqa: F401
except ImportError:
    logger.error("The package fakeredis is used for development only")


ENV_FILE = "env.ini"

config = ConfigParser()
config.read_file(open(join(dirname(__file__), ENV_FILE)))

DEFAULT_MIMETYPE = "text/plain"
DEVELOPMENT = config.get(section="Development", option="testing", fallback=False)


"""Testing env"""
if DEVELOPMENT:
    pass


"""Production env"""


@dataclass(frozen=True)
class RedisParams:
    redis_host: str = config.get(section="Redis", option="host", fallback="localhost")
    redis_port: int = config.getint(section="Redis", option="port", fallback=6379)
    redis_password: str = config.get(section="Redis", option="password", fallback="")


redis_db = Redis(host=RedisParams.redis_host, port=RedisParams.redis_port, password=RedisParams.redis_password)


@dataclass(frozen=True)
class VaultParams:
    vault_host: str = config.get(section="Vault", option="host", fallback="localhost")
    vault_port: int = config.getint(section="Vault", option="port", fallback=8200)


vault_client = VaultClient(url=f"http://{VaultParams.vault_host}:{VaultParams.vault_port}")


class DataParams:
    required_service: str = config.get(section="Data", option="required_service", fallback="terraform")
    common_params: List[str] = ["host", "username", "password"]
    list_params: List[str] = ["interfaces"]
    meta_params: List[str] = ["uuid", "createdAt", "expirationDate", "team"]
    temp_file_directory: str = "temp/"
