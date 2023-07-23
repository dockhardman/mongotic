from pymongo import MongoClient

from mongotic.orm import sessionmaker


def test_session_maker():
    Session_1 = sessionmaker()
    Session_2 = sessionmaker()
    assert (
        Session_1(bind_engine=MongoClient()) == Session_2(bind_engine=MongoClient())
    ) is False
