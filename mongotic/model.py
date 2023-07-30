from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Text, Type

from pydantic import BaseModel, PrivateAttr
from pydantic._internal import _model_construction

if TYPE_CHECKING:
    from mongotic.orm import Session

NOT_SET_SENTINEL = object()


class Operator(Enum):
    EQUAL = auto()

    def __str__(self):
        if self == Operator.EQUAL:
            return "=="
        else:
            raise NotImplementedError


class ModelFieldOperation(object):
    def __init__(self, model_field: "ModelField", operation: Operator, value: Any):
        self.model_field = model_field
        self.operation = operation
        self.value = value

    def __repr__(self) -> Text:
        return (
            "<ModelFieldOperation("
            + f"{self.model_field.field_name} {self.operation} {self.value}"
            ")>"
        )

    @classmethod
    def to_mongo_filter(
        cls, filters: List["ModelFieldOperation"], **kwargs
    ) -> Dict[Text, Any]:
        filter_dict: Dict[Text, Any] = {}

        for _filter in filters:
            if _filter.model_field.field_name not in filter_dict:
                filter_dict[_filter.model_field.field_name] = {}

            field_filter: Dict = filter_dict[_filter.model_field.field_name]

            if _filter.operation == Operator.EQUAL:
                field_filter.update({"$eq": _filter.value})

        return filter_dict


class ModelField(object):
    def __init__(self, field_name: Text, model_class: Type["MongoBaseModel"]):
        self.field_name = field_name
        self.model_class = model_class

    def __repr__(self) -> Text:
        return f"<ModelField(FieldName={self.field_name}, Bind={self.model_class.__name__})>"

    def __eq__(self, other: Any):
        return ModelFieldOperation(
            model_field=self, operation=Operator.EQUAL, value=other
        )


class MongoBaseModelMeta(_model_construction.ModelMetaclass):
    def __getattr__(cls, item: Text):
        try:
            return super().__getattr__(item)
        except AttributeError as e:
            if item in cls.__dict__["__annotations__"]:
                return ModelField(field_name=item, model_class=cls)
            else:
                raise e


class MongoBaseModel(BaseModel, metaclass=MongoBaseModelMeta):
    __databasename__: Text = NOT_SET_SENTINEL
    __tablename__: Text = NOT_SET_SENTINEL

    _id: Optional[Text] = PrivateAttr(None)
    _session: Optional["Session"] = PrivateAttr(None)

    def __setattr__(self, name: Text, value: Any) -> None:
        super().__setattr__(name, value)
        if self._session is not None and name not in ["_id", "_session"]:
            self._session._update_instances.append(tuple([self, name, value]))


if __name__ == "__main__":
    from datetime import datetime

    from pyassorted.datetime import aware_datetime_now
    from pydantic import Field
    from rich import print

    class User(MongoBaseModel):
        __databasename__ = "test"
        __tablename__ = "user"

        name: Text = Field(..., max_length=50)
        email: Text = Field(...)
        company: Optional[Text] = Field(None, max_length=50)
        age: Optional[int] = None
        created_at: Optional[datetime] = Field(..., default_factory=aware_datetime_now)
        updated_at: Optional[datetime] = Field(..., default_factory=aware_datetime_now)

    print(User.model_fields)
    new_user = User(
        name="John Doe", email="johndoe@example.com", company="test_company", age=30
    )
    new_user.name = "GGWP"
    print(new_user)
    # print("new_user:", new_user.name)
    # print(User.name)
    # print(User.name == "ggwp")
