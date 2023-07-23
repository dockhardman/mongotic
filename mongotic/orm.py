from typing import Any

from pymongo import MongoClient


def sessionmaker():
    def __init__(self, bind_engine: "MongoClient", **kwargs: Any):
        self.engine = bind_engine

    def query(self, *args: Any, **kwargs: Any):
        return

    def add(self, *args: Any, **kwargs: Any):
        return

    def commit(self, *args: Any, **kwargs: Any):
        return

    # use type to create a new Session class
    Session = type(
        "Session",
        (),
        {"__init__": __init__, "query": query, "add": add, "commit": commit},
    )

    return Session
