import logging
import os
from typing import Generator

import pytest
from pymongo import MongoClient

from mongotic import create_engine

logger = logging.getLogger("pytest")


@pytest.fixture(autouse=True)
def mongo_engine() -> Generator["MongoClient", None, None]:
    if "MONGO_CONNECTION_STRING" not in os.environ:
        raise Exception("Testing MONGO_CONNECTION_STRING environment variable not set.")

    mongo_conn_str = os.environ["MONGO_CONNECTION_STRING"]
    logger.debug(f"Connect to MongoDB: {mongo_conn_str}")

    engine = create_engine(mongo_conn_str)
    yield engine
    engine.close()
