from typing import Any, Optional, Text, Type

from pydantic import BaseModel, PrivateAttr
from pydantic._internal import _model_construction

NOT_SET_SENTINEL = object()


class ModelFieldOperation(object):
    def __init__(self, model_field: "ModelField", operation: Text, value: Any):
        self.model_field = model_field
        self.operation = operation
        self.value = value

    def __repr__(self) -> Text:
        return f"<ModelFieldOperation({self.model_field.field_name} {self.operation} {self.value})>"


class ModelField(object):
    def __init__(self, field_name: Text, model_class: Type["MongoBaseModel"]):
        self.field_name = field_name
        self.model_class = model_class

    def __repr__(self) -> Text:
        return f"<ModelField(FieldName={self.field_name}, Bind={self.model_class.__name__})>"

    def __eq__(self, other: Any):
        return ModelFieldOperation(model_field=self, operation="==", value=other)


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
    print("new_user:", new_user.name)
    print(User.name)
    print(User.name == "ggwp")
