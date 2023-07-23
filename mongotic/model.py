from pydantic import BaseModel

NOT_SET_SENTINEL = object()


class MongoBaseModel(BaseModel):
    __tablename__ = NOT_SET_SENTINEL
    __databasename__ = NOT_SET_SENTINEL


if __name__ == "__main__":
    model = MongoBaseModel()
    print(model.model_dump())
