from typing import Any, List, Protocol, Text, Type

from pymongo import MongoClient
from typing_extensions import ParamSpec

from mongotic.model import NOT_SET_SENTINEL, MongoBaseModel

P = ParamSpec("P")


class QuerySet:
    def filter_by(self, *args: Any, **kwargs: Any) -> "QuerySet":
        ...

    def limit(self, *args: Any, **kwargs: Any) -> "QuerySet":
        ...

    def offset(self, *args: Any, **kwargs: Any) -> "QuerySet":
        ...

    def first(self, *args: Any, **kwargs: Any) -> "MongoBaseModel":
        ...

    def all(self, *args: Any, **kwargs: Any) -> List["MongoBaseModel"]:
        ...


class Session(Protocol):
    engine: "MongoClient"

    def __init__(self, bind_engine: MongoClient, **kwargs: Any):
        ...

    def query(
        self, base_model: Type["MongoBaseModel"], *args: Any, **kwargs: Any
    ) -> QuerySet:
        ...

    def add(self, model_instance: "MongoBaseModel", *args: Any, **kwargs: Any) -> Text:
        ...

    def update(
        self, model_instance: "MongoBaseModel", *args: Any, **kwargs: Any
    ) -> Text:
        ...

    def delete(
        self, model_instance: "MongoBaseModel", *args: Any, **kwargs: Any
    ) -> Text:
        ...

    def commit(self, *args: Any, **kwargs: Any) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...


def sessionmaker(bind: "MongoClient") -> Type[Session]:
    class _Session:
        def __init__(self, *args, **kwargs: Any):
            self.engine = bind

        def query(
            self, base_model: Type["MongoBaseModel"], *args: Any, **kwargs: Any
        ) -> QuerySet:
            return

        def add(
            self, model_instance: "MongoBaseModel", *args: Any, **kwargs: Any
        ) -> Text:
            if model_instance.__databasename__ is NOT_SET_SENTINEL:
                raise ValueError("Database name is not set")
            if model_instance.__tablename__ is NOT_SET_SENTINEL:
                raise ValueError("Table name is not set")

            db = self.engine[model_instance.__databasename__]
            col = db[model_instance.__tablename__]

            doc = model_instance.model_dump()
            result = col.insert_one(doc)

            model_instance._id = str(result.inserted_id)
            return model_instance._id

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
