from typing import Optional, Text

from pydantic import BaseModel, PrivateAttr

NOT_SET_SENTINEL = object()


class MongoBaseModel(BaseModel):
    __databasename__: Text = NOT_SET_SENTINEL
    __tablename__: Text = NOT_SET_SENTINEL

    _id: Optional[Text] = PrivateAttr(None)


if __name__ == "__main__":
    model = MongoBaseModel()
    print(model.model_dump())
