from typing import NamedTuple

class Connection(NamedTuple):
    name: str
    default: bool
    driver: str
    dialect: str
    host: str
    port: int
    database: str
    username: str
    password: str
    prefix: str
    url: str
