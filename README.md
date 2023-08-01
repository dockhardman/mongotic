# mongotic

The concept of MongoDB, SQLAlchemy, and Pydantic combined together in one simple and effective solution. It enables you to use SQLAlchemy query syntax with MongoDB, and allows you to define your data models using Pydantic.

## Overview

The `mongotic` library is designed to make working with MongoDB as seamless as possible by using familiar tools and patterns from the SQLAlchemy and Pydantic ecosystems. It provides a consistent and expressive way to interact with MongoDB collections, and utilizes Pydantic for validation and data definition.

## Features

- **Easy integration**: Use the familiar SQLAlchemy ORM patterns with MongoDB.
- **Data Validation**: Utilize Pydantic's powerful schema definition for data validation and serialization.
- **Type Checking**: Benefit from type checking and autocomplete in IDEs due to static type definitions.

## Installation

You can install the package from your preferred package manager. For instance:

```bash
pip install mongotic
```

## Usage

Here's a simple example to help you get started with `mongotic`. This example covers basic operations like adding, querying, updating, and deleting documents in a MongoDB collection.

```python
from typing import Optional, Text

from pydantic import Field
from pymongo import MongoClient

from mongotic.model import MongoBaseModel
from mongotic.orm import Session as SessionType
from mongotic.orm import sessionmaker


class User(MongoBaseModel):
    __databasename__ = "test_database"
    __tablename__ = "user"

    name: Text = Field(..., max_length=50)
    email: Text = Field(...)
    company: Optional[Text] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=200)


def add_operation(session: "SessionType"):
    new_user = User(
        name="Allen Chou", email="allen.chou@example.com", company="A company", age=30
    )
    session.add(new_user)
    session.commit()


def query_operation(session: "SessionType"):
    user = session.query(User).first()
    assert user

    users = session.query(User).all()
    assert len(users) > 0

    users = session.query(User).filter(User.email == "allen.chou@example.com").all()
    assert len(users) > 0

    users = session.query(User).filter(email="allen.chou@example.com").all()
    assert len(users) > 0

    users = session.query(User).filter_by(email="allen.chou@example.com").all()
    assert len(users) > 0

    users = session.query(User).filter(User.company == "ERROR_COMPANY").all()
    assert len(users) == 0


def update_operation(session: "SessionType"):
    alice = session.query(User).filter_by(email="allen.chou@example.com").first()

    alice.email = "new.allen.chou@example.com"

    session.commit()


def delete_operation(session: "SessionType"):
    user = session.query(User).filter_by(email="allen.chou@example.com").first()

    session.delete(user)

    session.commit()


if __name__ == "__main__":
    mongo_engine = MongoClient("mongodb://localhost:27017")
    db = mongo_engine[User.__databasename__]
    if User.__tablename__ not in db.list_collection_names():
        db.create_collection(User.__tablename__)

    Session = sessionmaker(bind=mongo_engine)
    session = Session()

    add_operation(session)
    query_operation(session)
    update_operation(session)
    delete_operation(session)
```

## Contributing

TODO:

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have suggestions, please open an issue, or feel free to reach out directly.
