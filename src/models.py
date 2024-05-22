import datetime
from random import randint
# from typing import Self, TYPE_CHECKING, dataclass_transform  # Python 3.11
from typing import Optional, List

from sqlalchemy import DateTime, Integer, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression
from streamlit.logger import get_logger

import const

log = get_logger(__name__)

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
        DateTime,
        # server_default=text("CURRENT_TIMESTAMP"),  # GMT
        # server_default=text("(datetime(CURRENT_TIMESTAMP, 'localtime'))"),
        server_default=text("(datetime('now', 'localtime'))"),
        nullable=False,
    )
    author: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=const.STATUS_ALIVE)

    def __repr__(self):
        return f"{self.__class__} object id={self.id}"

    @staticmethod
    def get_db_session() -> Session:
        import database
        db_session = database.session
        # db_session = database.conn.session
        # if "db_session" not in st.session_state:
        #     st.session_state["db_session"] = database.conn.session
        # db_session = st.session_state.get("db_session", database.conn.session)
        # if db_session is None:
        #     raise RuntimeError()
        log.debug(f"get_db_session:{db_session}")
        return db_session

    # @classmethod
    # def get(cls, id_) -> "typing.Self":
    #     db_session = cls.get_db_session()
    #     return db_session.get(cls, id_)

    @classmethod
    def get(cls, id_):
        db_session = cls.get_db_session()
        result: Optional[cls] = db_session.get(cls, id_)
        return result

    @classmethod
    def get_or_create(cls, id_, **kwargs):
        result: Optional[cls] = cls.get(id_)
        return result if result else cls(**kwargs)

    @classmethod
    def query(cls) -> Query:
        db_session = cls.get_db_session()
        return db_session.query(cls)

    @classmethod
    def list(cls, *expressions: BinaryExpression, order_by=None):
        query: Query = cls.query()
        for expr in expressions:
            if expr.left == cls.status:
                break
        else:
            expressions = (cls.status == const.STATUS_ALIVE, *expressions)
        query = query.filter(*expressions)
        if order_by:
            query = query.order_by(order_by)
        else:
            query = query.order_by(cls.created.desc(), cls.id.desc())

        # result: List[cls] = query.all()
        # return result
        return query.all()

    def save(self):
        db_session = self.get_db_session()
        db_session.add(self)
        db_session.flush()
        db_session.commit()
        # return self.get(self.id)
        return self

    @classmethod
    def delete_by_id(cls, id_):
        db_session = cls.get_db_session()
        db_session.get(cls, id_).status = const.STATUS_DELETE
        db_session.commit()

    def delete(self):
        db_session = self.get_db_session()
        self.status = const.STATUS_DELETE
        db_session.add(self)
        db_session.commit()

    def is_new(self):
        return self.id is None

    def __bool__(self):
        return not self.is_new()


class UserStoryModel(BaseModel):
    __tablename__ = "user_story"
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
    business_ctx: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
    acceptance_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
    ddd_glossary: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
    ddd_model: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
    tdd_task: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
    tdd_code: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")

    # def __init__(self, title: str, content: str, business_ctx: str):
    #     super().__init__(title=title, content=content, business_ctx=business_ctx)


def test_case():
    import database
    database.init_database()

    obj_new = UserStoryModel(
        title="test",
    )
    print("obj_new.id:", obj_new.id)
    obj_created = obj_new.save()
    obj_id = obj_created.id
    obj_created.delete()
    print("obj_created.id:", obj_id)
    obj_get = UserStoryModel.get(obj_id)
    print("obj_get.title:", obj_get.title)
    print("obj_get.status:", obj_get.status)
    assert obj_created.id == obj_get.id
    assert obj_created.title == obj_get.title
    assert obj_created.status == obj_get.status

    # obj_list: List[BusinessCtxModel] = BusinessCtxModel.list(
    #     BusinessCtxModel.status == const.STATUS_DELETE
    # )
    obj_list: List[UserStoryModel] = UserStoryModel.query().filter(
        UserStoryModel.status == const.STATUS_DELETE
    ).all()
    print(obj_list)
    # for obj in obj_list:
    #     print(obj.id, obj.created, obj.title)
    assert obj_id in [obj.id for obj in obj_list]


def test_sqlalchemy_expression():
    expr: BinaryExpression = UserStoryModel.status == const.STATUS_ALIVE
    print(type(expr))
    print(expr.left)
    assert expr.left == UserStoryModel.status
    # for key in dir(expr):
    #     print(key, getattr(expr, key, None))
    query: Query = UserStoryModel.get_db_session().query(UserStoryModel)
    print(type(query))


if __name__ == "__main__":
    test_case()
    test_sqlalchemy_expression()
