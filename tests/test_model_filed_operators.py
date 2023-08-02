from datetime import datetime
from typing import Optional, Text

from pyassorted.datetime import aware_datetime_now
from pyassorted.string import rand_str
from pydantic import Field
from pymongo import MongoClient

from mongotic.model import MongoBaseModel
from mongotic.orm import sessionmaker

test_company = f"test_{rand_str(10)}"


class User(MongoBaseModel):
    __databasename__ = "test"
    __tablename__ = "user"

    name: Text = Field(..., max_length=50)
    email: Text = Field(...)
    company: Optional[Text] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=200)
    created_at: Optional[datetime] = Field(..., default_factory=aware_datetime_now)
    updated_at: Optional[datetime] = Field(..., default_factory=aware_datetime_now)


def test_init_documents(mongo_engine: "MongoClient"):
    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    new_user = User(
        name="Alice Moe",
        email="alice.moe@example.com",
        company=test_company,
        age=25,
    )
    session.add(new_user)
    session.commit()


def test_clean_documents(mongo_engine: "MongoClient"):
    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    users = session.query(User).filter_by(company=test_company).limit(10).all()

    for user in users:
        session.delete(user)

    session.commit()
