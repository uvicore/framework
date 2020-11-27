from abc import ABC
from dataclasses import dataclass

@dataclass
class Connection(ABC):
    name: str
    #default: bool
    driver: str
    dialect: str
    host: str
    port: int
    database: str
    username: str
    password: str
    prefix: str
    metakey: str
    url: str
