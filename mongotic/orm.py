from typing import Any, Protocol, Type

from pymongo import MongoClient
from typing_extensions import ParamSpec

P = ParamSpec("P")


class Session(Protocol):
    engine: "MongoClient"

    def __init__(self, bind_engine: MongoClient, **kwargs: Any):
        ...

    def query(self, *args: Any, **kwargs: Any):
        ...

    def add(self, *args: Any, **kwargs: Any):
        ...

    def commit(self, *args: Any, **kwargs: Any) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...


def sessionmaker() -> Type[Session]:
    class _Session:
        def __init__(self, bind_engine: "MongoClient", **kwargs: Any):
            self.engine = bind_engine

        def query(self, *args: Any, **kwargs: Any):
            return

        def add(self, *args: Any, **kwargs: Any):
            return

        def commit(self, *args: Any, **kwargs: Any) -> None:
            with self.engine.start_session() as session:
                pass

        def __enter__(self):
            self.session = self.engine.start_session()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.session.end_session()
            self.session = None

    return _Session
