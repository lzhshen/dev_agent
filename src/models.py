import datetime
import functools
from random import randint
# from typing import Self, TYPE_CHECKING, dataclass_transform  # Python 3.11
from typing import Optional, List

from sqlalchemy import DateTime, Integer, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import Session
import streamlit as st

import const

# Python 3.11
# if TYPE_CHECKING:
#     # this gives any class that derives from Base some simple type hints
#     @dataclass_transform()
#     class Base(DeclarativeBase):
#         pass
# else:
#     # dataclass_transform should never mess with runtime codes to avoid behavior changes
#     class Base(DeclarativeBase):
#         pass


class BaseModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    uuid: Mapped[int] = mapped_column(
        Integer, index=True, unique=True, nullable=False, default=lambda: randint(1, 4_294_967_295))
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=const.STATUS_ALIVE)

    @staticmethod
    def get_db_session() -> Session:
        # import database
        # db_session = database.conn.session
        import database
        if "db_session" not in st.session_state:
            st.session_state["db_session"] = database.conn.session
        db_session = st.session_state.get("db_session", database.conn.session)
        print("get_db_session:", db_session)
        return db_session

    # @classmethod
    # def get(cls, id_) -> "typing.Self":
    #     db_session = cls.get_db_session()
    #     return db_session.get(cls, id_)

    @classmethod
    def get(cls, id_):
        with cls.get_db_session() as db_session:
            result: Optional[cls] = db_session.get(cls, id_)
            return result

    @classmethod
    def filter(cls, *filters):
        db_session = cls.get_db_session()
        result: Optional[List[cls]] = db_session.query(cls).filter(*filters).all()
        return result

    def save(self):
        with self.get_db_session() as db_session:
            db_session.add(self)
            db_session.flush()
            db_session.commit()
            return self.get(self.id)

    @classmethod
    def delete_by_id(cls, id_):
        with cls.get_db_session() as db_session:
            db_session.get(cls, id_).status = const.STATUS_DELETE
            db_session.commit()

    def delete(self):
        self.status = const.STATUS_DELETE
        self.delete_by_id(self.id)


class BusinessCtxModel(BaseModel):
    __tablename__ = "business_ctx"
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")


class UserStoryModel(BaseModel):
    __tablename__ = "user_story"
    business_ctx_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")


class AcceptanceCriteriaModel(BaseModel):
    __tablename__ = "acceptance_criteria"
    user_story_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")


def test_case():
    obj_new = BusinessCtxModel(
        title="test",
    )
    obj_created = obj_new.save()
    obj_created.delete()
    obj_id = obj_created.id
    print("obj_created.id:", obj_created.id)
    obj_get = BusinessCtxModel.get(obj_id)
    print("obj_get.title:", obj_get.title)
    print("obj_get.status:", obj_get.status)
    assert obj_created.id == obj_get.id
    assert obj_created.title == obj_get.title
    assert obj_created.status == obj_get.status


if __name__ == "__main__":
    test_case()
