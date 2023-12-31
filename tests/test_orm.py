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


def test_session_maker(mongo_engine: "MongoClient"):
    Session_1 = sessionmaker(bind=mongo_engine)
    Session_2 = sessionmaker(bind=mongo_engine)
    assert (Session_1() == Session_2()) is False


def test_add_operation(mongo_engine: "MongoClient"):
    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    new_user = User(
        name="John Doe", email="johndoe@example.com", company=test_company, age=30
    )
    session.add(new_user)
    session.commit()


def test_query_operation(mongo_engine: "MongoClient"):
    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    user = session.query(User).first()
    assert user

    users = session.query(User).all()
    assert len(users) > 0

    users = session.query(User).filter(User.company == test_company).all()
    assert len(users) > 0

    users = session.query(User).filter(company=test_company).all()
    assert len(users) > 0

    users = session.query(User).filter_by(company=test_company).all()
    assert len(users) > 0

    users = session.query(User).filter(User.company == "ERROR_COMPANY").all()
    assert len(users) == 0


def test_update_operation(mongo_engine: "MongoClient"):
    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    alice = session.query(User).filter_by(company=test_company).first()

    alice.email = "new_johndoe@example.com"

    session.commit()


def test_delete_operation(mongo_engine: "MongoClient"):
    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    user = session.query(User).filter_by(company=test_company).first()

    session.delete(user)

    session.commit()
