from typing import Any, List, Protocol, Text, Type

from pymongo import MongoClient
from typing_extensions import ParamSpec

from mongotic.exceptions import NotFound
from mongotic.model import (
    NOT_SET_SENTINEL,
    ModelField,
    ModelFieldOperation,
    MongoBaseModel,
)

P = ParamSpec("P")


class QuerySet:
    def __init__(
        self,
        orm_model: Type["MongoBaseModel"],
        *args: Any,
        engine: "MongoClient",
        **kwargs: Any
    ):
        self.orm_model = orm_model
        self.engine = engine

        if self.orm_model.__databasename__ is NOT_SET_SENTINEL:
            raise ValueError("Database name is not set")
        if self.orm_model.__tablename__ is NOT_SET_SENTINEL:
            raise ValueError("Table name is not set")

        self._db_name: Text = self.orm_model.__databasename__
        self._col_name: Text = self.orm_model.__tablename__
        self._limit = 5
        self._offset = 0
        self._filters: List["ModelFieldOperation"] = []

    def filter(
        self, *model_field_operations: "ModelFieldOperation", **kwargs: Any
    ) -> "QuerySet":
        if not model_field_operations and not kwargs:
            raise ValueError("No filter is provided")

        self._filters.extend(model_field_operations)

        for k, v in kwargs.items():
            self._filters.append(
                ModelField(field_name=k, model_class=self.orm_model) == v
            )

        return self

    def filter_by(self, **kwargs: Any) -> "QuerySet":
        for k, v in kwargs.items():
            self._filters.append(
                ModelField(field_name=k, model_class=self.orm_model) == v
            )
        return self

    def limit(self, *args: Any, **kwargs: Any) -> "QuerySet":
        ...

    def offset(self, *args: Any, **kwargs: Any) -> "QuerySet":
        ...

    def first(self, *args: Any, **kwargs: Any) -> "MongoBaseModel":
        collection = self.engine[self._db_name][self._col_name]

        filter_body = ModelFieldOperation.to_mongo_filter(filters=self._filters)
        doc_raw = collection.find_one(filter=filter_body)
        if not doc_raw:
            raise NotFound

        doc_raw["_id"] = str(doc_raw["_id"])
        doc = self.orm_model(**doc_raw)
        return doc

    def all(self, *args: Any, **kwargs: Any) -> List["MongoBaseModel"]:
        docs: List["MongoBaseModel"] = []

        collection = self.engine[self._db_name][self._col_name]

        filter_body = ModelFieldOperation.to_mongo_filter(filters=self._filters)

        for _doc in collection.find(filter_body).skip(self._offset).limit(self._limit):
            _doc["_id"] = str(_doc["_id"])
            docs.append(self.orm_model(**_doc))

        return docs


class Session(Protocol):
    engine: "MongoClient"

    def __init__(self, bind_engine: MongoClient, **kwargs: Any):
        ...

    def query(
        self, orm_model: Type["MongoBaseModel"], *args: Any, **kwargs: Any
    ) -> QuerySet:
        ...

    def add(self, instance: "MongoBaseModel", *args: Any, **kwargs: Any) -> Text:
        ...

    def update(self, instance: "MongoBaseModel", *args: Any, **kwargs: Any) -> Text:
        ...

    def delete(self, instance: "MongoBaseModel", *args: Any, **kwargs: Any) -> Text:
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
            self, orm_model: Type["MongoBaseModel"], *args: Any, **kwargs: Any
        ) -> QuerySet:
            return QuerySet(orm_model=orm_model, engine=self.engine, *args, **kwargs)

        def add(self, instance: "MongoBaseModel", *args: Any, **kwargs: Any) -> Text:
            if instance.__databasename__ is NOT_SET_SENTINEL:
                raise ValueError("Database name is not set")
            if instance.__tablename__ is NOT_SET_SENTINEL:
                raise ValueError("Table name is not set")

            db = self.engine[instance.__databasename__]
            col = db[instance.__tablename__]

            doc = instance.model_dump()
            result = col.insert_one(doc)

            instance._id = str(result.inserted_id)
            return instance._id

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
