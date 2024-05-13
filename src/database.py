from typing import Optional
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
import streamlit as st
from streamlit.logger import get_logger
from streamlit.connections.sql_connection import SQLConnection

log = get_logger(__name__)

conn: Optional[SQLConnection]
engine: Optional[Engine] = None
session: Optional[Session] = None


def init_database():
    log.debug("init_database")
    init_database_engine()
    init_database_session()
    create_table()
    return


def init_database_engine():
    global conn, engine

    conn = st.connection(
        'database',
        type='sql',
        pool_pre_ping=True,
        # autocommit=True,
    )

    if "db_engine" in st.session_state:
        engine = st.session_state["db_engine"]
    else:
        engine = conn.engine
        st.session_state["db_engine"]: Engine = engine
        log.info("create database engine")


def init_database_session():
    global session

    session_maker = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    if "db_session" in st.session_state:
        session = st.session_state["db_session"]
    else:
        # session = conn.session
        session = session_maker()
        st.session_state["db_session"]: Session = session
        log.info("create database session")


@st.cache_resource
def create_table():
    reset_table = st.secrets.get("reset_table")
    fake_data = st.secrets.get("fake_data")
    log.debug(f"create_table reset_table={reset_table} fake_data={fake_data}")

    # engine = conn.engine
    # session = conn.session

    from models import BaseModel
    if reset_table:
        BaseModel.metadata.drop_all(bind=engine)
        log.info("reset_table")
    BaseModel.metadata.create_all(bind=engine)
    log.info("create_table")

    if fake_data:
        generate_fake_data()
        log.info("generate_fake_data")
    return


def generate_fake_business_ctx():
    from models import BusinessCtxModel
    business_ctx_model = BusinessCtxModel(
        title=f"业务背景",
        content="整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；",
    )
    return business_ctx_model.save()


def generate_fake_user_story(business_ctx_id):
    from models import UserStoryModel
    user_story_model = UserStoryModel(
        business_ctx_id=business_ctx_id,
        title=f"获取学位的进度",
        content="""作为学校的教职员工（As a faculty），
我希望学生可以根据录取通知将学籍注册到教学计划上（I want the student to be able to enroll in an academic program with given offer），
从而我可以跟踪他们的获取学位的进度（So that I can track their progress）""",
    )
    return user_story_model.save()


def generate_fake_acceptance_criteria(user_story_id):
    from models import AcceptanceCriteriaModel
    AcceptanceCriteriaModel(
        user_story_id=user_story_id,
        title=f"验收标准",
        content=f"""1. 场景1：正常注册
Given: 学生收到电子录取通知，上面有学号和登录信息
When: 学生使用学号和身份信息登录学籍管理系统
Then: 系统显示注册页面，学生按照录取通知完成注册，系统自动关联学生信息

2. 场景2：身份验证
Given: 学生登录后，系统要求上传身份证件
When: 学生上传清晰的身份证照片
Then: 系统验证通过，学生继续完成注册流程

3. 场景3：教职员工查看进度
Given: 教职员工登录系统进入学生管理界面
When: 教职员工搜索或选择特定学生
Then: 系统显示该学生的课程进度、成绩和毕业要求完成情况，教职工可追踪学生学习进度
""",
    ).save()
    return


def generate_fake_data():
    business_ctx_model = generate_fake_business_ctx()
    user_story = generate_fake_user_story(business_ctx_model.id)
    generate_fake_acceptance_criteria(user_story.id)


def test_case():
    init_database_engine()
    init_database_session()

    import contextlib

    @contextlib.contextmanager
    def transaction(_session):
        if not _session.in_transaction():
            with _session.begin():
                yield _session
        else:
            yield

    with transaction(conn.session) as s1:
        with transaction(conn.session) as s2:
            print(s1)
            print(s2)
            print("#" * 10)

    with session as s1:
        with session as s2:
            print(s1)
            print(s2)
            print("^" * 10)

    class SessionCtx:
        def __enter__(self):
            if "db_session" not in st.session_state:
                st.session_state["db_session"] = session
            return st.session_state.get("db_session", session)

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


def test_create_table():
    if __name__ == "__main__":
        log.warning("only not __main__")
        return
    log.info("test_create_table")
    init_database_engine()
    init_database_session()
    create_table()


if __name__ == "__main__":
    test_case()
