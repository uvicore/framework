from uvicore.typing import Dict

class Connection(Dict):
    """Database Connection Definition"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    name: str
    backend: str
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
    is_async: bool



#from abc import ABC
#from dataclasses import dataclass
# @dataclass
# class Connection(ABC):
#     name: str
#     #default: bool
#     driver: str
#     dialect: str
#     host: str
#     port: int
#     database: str
#     username: str
#     password: str
#     prefix: str
#     metakey: str
#     url: str

