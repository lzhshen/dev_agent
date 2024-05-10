import functools
from typing import Optional, Type

from sqlalchemy import create_engine, func, select, Engine
from sqlalchemy.orm import Session, sessionmaker
import streamlit as st

from models import BaseModel, BusinessCtxModel, UserStoryModel, AcceptanceCriteriaModel

conn = st.connection(
    'database',
    type='sql',
    pool_pre_ping=True,
    # autocommit=True,
)
if "db_session" not in st.session_state:
    st.session_state["db_session"] = conn.session


@st.cache_resource
def init_database():
    print("init_database")
    engine = conn.engine
    session = conn.session
    reset_table = st.secrets.get("reset_table")
    fake_data = st.secrets.get("fake_data")
    if reset_table:
        BaseModel.metadata.drop_all(bind=engine)
        print("reset_table")
    BaseModel.metadata.create_all(bind=engine)
    print("create_table")
    if fake_data:
        generate_fake_data()
        print("generate_fake_data")
    return session


def generate_fake_business_ctx():
    business_ctx_model = BusinessCtxModel(
        title=f"业务背景",
        content="整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；",
    )
    return business_ctx_model.save()


def generate_fake_user_story(business_ctx_id):
    user_story_model = UserStoryModel(
        business_ctx_id=business_ctx_id,
        title=f"获取学位的进度",
        content="""作为学校的教职员工（As a faculty），
我希望学生可以根据录取通知将学籍注册到教学计划上（I want the student to be able to enroll in an academic program with given offer），
从而我可以跟踪他们的获取学位的进度（So that I can track their progress）""",
    )
    return user_story_model.save()


def generate_fake_data():
    business_ctx_model = generate_fake_business_ctx()
    generate_fake_user_story(business_ctx_model.id)


init_database()


# @st.cache_resource
# def get_database_engine() -> Engine:
#     print("get_database_engine")
#     # engine = create_engine(url, echo=False)
#     # create_table(engine, reset_table)
#     return conn.engine
#
#
# def create_table():
#     engine = get_database_engine()
#     reset_table = st.secrets.get("reset_table")
#     if reset_table:
#         BaseModel.metadata.drop_all(bind=engine)
#     BaseModel.metadata.create_all(bind=engine)
#
#
# def get_database_session(config: dict) -> Session:
#     url = config["url"]
#     reset_table = config["reset_table"]
#     fake_data = config["fake_data"]
#     engine = get_database_engine(url, reset_table)
#     sess = sessionmaker(bind=engine)
#     session = sess()
#     if fake_data:
#         generate_fake_data(session)
#     return session
#
#
# def clear_table(session: Session) -> str:
#     success = "rollback"
#     session.query(BusinessCtxModel).delete()
#     session.query(UserStoryModel).delete()
#     session.query(AcceptanceCriteriaModel).delete()
#     try:
#         session.commit()
#     except Exception as e:
#         print(e)
#         session.rollback()
#     else:
#         success = "commit"
#     return success
#
#
# def get_single_business_context(session: Session, id_: int):
#     business_context = session.get(BusinessCtxModel, id_)
#     return business_context
#
#
# def generate_fake_business_context(session: Session):
#     # success = "rollback"
#     # business_ctx = BusinessCtxModel(
#     #     title=f"业务背景",
#     #     content="整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；",
#     # )
#     # session.add(business_ctx)
#     # try:
#     #     session.commit()
#     # except Exception as e:
#     #     print(e)
#     #     session.rollback()
#     # else:
#     #     success = "commit"
#     # return success
#     business_ctx_model = BusinessCtxModel(
#         title=f"业务背景",
#         content="整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；",
#     )
#     return business_ctx_model.save()
#
#
# def get_all_user_stories(session: Session):
#     user_stories = session.query(UserStoryModel).all()
#     return user_stories
#
#
# def get_all_user_stories_sorted_desc(session: Session, by: str = "created"):
#     user_stories = session.query(UserStoryModel).order_by(getattr(UserStoryModel, by).desc()).all()
#     return user_stories
#
#
# def get_all_user_stories_sorted_asc(session: Session, by: str = "created"):
#     user_stories = session.query(UserStoryModel).order_by(getattr(UserStoryModel, by).asc()).all()
#     return user_stories
#
#
# def get_single_user_story(session: Session, id_: int) -> Optional[Type[UserStoryModel]]:
#     user_story = session.get(UserStoryModel, id_)
#     return user_story
#
#
# def generate_fake_user_story(session: Session, business_ctx_id) -> str:
# #     success = "rollback"
# #     user_story = UserStoryModel(
# #         business_ctx_id=business_ctx_id,
# #         title=f"获取学位的进度",
# #         content="""作为学校的教职员工（As a faculty），
# # 我希望学生可以根据录取通知将学籍注册到教学计划上（I want the student to be able to enroll in an academic program with given offer），
# # 从而我可以跟踪他们的获取学位的进度（So that I can track their progress）""",
# #     )
# #     session.add(user_story)
# #     try:
# #         session.commit()
# #     except Exception as e:
# #         print(e)
# #         session.rollback()
# #     else:
# #         success = "commit"
# #     return success
#     user_story_model = UserStoryModel(
#         business_ctx_id=business_ctx_id,
#         title=f"获取学位的进度",
#         content="""作为学校的教职员工（As a faculty），
# 我希望学生可以根据录取通知将学籍注册到教学计划上（I want the student to be able to enroll in an academic program with given offer），
# 从而我可以跟踪他们的获取学位的进度（So that I can track their progress）""",
#     )
#     return user_story_model.save()
#
#
# def delete_user_story(session: Session, id_: int = None) -> str:
#     success = "rollback"
#     if id_:
#         session.query(UserStoryModel).filter(UserStoryModel.id == id_).delete()
#         try:
#             session.commit()
#         except Exception as e:
#             print(e)
#             session.rollback()
#         else:
#             success = "commit"
#     return success
#
#
# def get_oldest_user_story(session: Session):
#     user_story = session.query(UserStoryModel).order_by(UserStoryModel.created.asc()).first()
#     return user_story
#
#
# def get_newest_user_story(session: Session):
#     user_story = session.query(UserStoryModel).order_by(UserStoryModel.created.desc()).first()
#     return user_story
#
#
# def get_random_user_story(session: Session):
#     user_story = session.query(UserStoryModel).order_by(func.random()).first()
#     return user_story
#
#
# def get_user_story_count(session: Session):
#     count = session.scalar(select(func.count(UserStoryModel.id)))
#     return count
#
#
# def generate_fake_data(session):
#     business_context_model = generate_fake_business_context(session)
#     generate_fake_user_story(session, business_context_model.id)


def test_case():
    # init_database()

    import contextlib

    @contextlib.contextmanager
    def transaction(session):
        if not session.in_transaction():
            with session.begin():
                yield session
        else:
            yield

    with transaction(conn.session) as s1:
        with transaction(conn.session) as s2:
            print(s1)
            print(s2)
            print("#" * 10)

    session = conn.session
    with session as s1:
        with session as s2:
            print(s1)
            print(s2)
            print("^" * 10)

    class SessionCtx:
        def __enter__(self):
            if "db_session" not in st.session_state:
                st.session_state["db_session"] = conn.session
            return st.session_state.get("db_session", conn.session)

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type and exc_val and exc_tb:
                return False
            if "db_session" in st.session_state:
                st.session_state["db_session"].commit()
                del st.session_state["db_session"]

    with SessionCtx() as s1:
        with SessionCtx() as s2:
            print(s1)
            print(s2)
            print("^" * 10)

if __name__ == "__main__":
    test_case()
