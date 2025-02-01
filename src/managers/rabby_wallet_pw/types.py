from logging import Logger
from typing import TypedDict
from typing_extensions import NotRequired


class Config(TypedDict):
    logger: Logger
    store_identificator: str


class BaseData(TypedDict):
    mnemonic: NotRequired[str]
    private_key: NotRequired[str]
    password: str
    proxy_type: NotRequired[str]
    proxy: NotRequired[str]
    address: NotRequired[str]
    public_key: NotRequired[str]


class ParsedData(BaseData):
    serial_number: str


class ParsedWithUserData(ParsedData):
    user_id: str
