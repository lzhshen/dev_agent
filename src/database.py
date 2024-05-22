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


def generate_fake_data():
    from models import UserStoryModel
    user_story_fake_data = {
        # "教职员工发放录取通知书": "作为 教职员工，我想要 发放录取通知书时同步创建学生的账号，以便 管理和跟踪学生的入学流程。",
        "学生查询账号": "作为 学生，我想要 使用我的身份信息查询预创建的账号，以便 确认我的入学资格并获取系统访问权限。",
        "新生登录账号": "作为 新生，我需要 登录我的账号，以便 查看和确认录取通知书上的详细信息。",
        "学生登录账号": "作为 学生，我想要 在报道注册时登录我的学籍管理系统账号，以便 完成学年的注册流程。",
        "系统管理员监控账号激活和注册情况": "作为 系统管理员，我想要 监控学生的账号激活和注册情况，以便 确保所有新生都能顺利开始他们的学习旅程。",
        "教职员工查看学生的注册状态": "作为 教职员工，我想要 能够查看学生的注册状态，以便 追踪哪些学生已经完成注册，哪些学生需要跟进。",
        "学生更新个人信息": "作为 学生，我想要 在系统中更新我的个人信息，以便 确保学校拥有最新的联系信息。",
        "教职员工验证学生的注册信息": "作为 教职员工，我需要 能够验证学生的注册信息，以便 核实其资格并处理任何异常情况。",
    }
    business_ctx = "整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；" \
                   "学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；"

    for title, content in user_story_fake_data.items():
        user_story_model = UserStoryModel()
        user_story_model.title = title
        user_story_model.ddd_glossary = """概念	定义	Archetype
学生注册验证	教职员工核实学生注册信息的过程，确保符合资格并处理异常情况。	Moment-interval
学生	参与注册验证过程的个人，通常是高等教育机构的在读或申请就读的学生。	Party-place-thing (Role: 学生)
教职员工	负责验证学生注册信息的教职工，可能包括教务人员、辅导员等。	Party-place-thing (Role: 教职员工)
注册信息	包含学生个人信息、学术资格、课程选择等用于验证的详细数据。	Description
学生资格	学生满足继续学业或入学所需的一系列条件，如年龄、学历、考试成绩等。	Description
异常情况	在验证过程中发现的问题，如信息不一致、资格不符等，需要处理的情况。	Moment-interval
注册时段	学生可以提交注册信息的时间段，通常在学年开始前设定。	Moment-interval
验证结果	验证过程后的决定，可能是合格、不合格或其他特殊状态。	Description"""
        user_story_model.content = content
        user_story_model.business_ctx = business_ctx
        user_story_model.save()

    user_story_model = UserStoryModel()
    user_story_model.title = "获取学位的进度"
    user_story_model.content = """作为学校的教职员工（As a faculty），
# 我希望学生可以根据录取通知将学籍注册到教学计划上（I want the student to be able to enroll in an academic program with given offer），
# 从而我可以跟踪他们的获取学位的进度（So that I can track their progress）"""
    user_story_model.business_ctx = business_ctx
    user_story_model.acceptance_criteria = """1. 场景1：正常注册
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
"""
    user_story_model.ddd_glossary = """业务概念	定义
教职员工	在学校中负责教学和管理工作的人员，包括教师、辅导员等
录取通知	学校向被录取的学生发出的正式文件，确认其已被接受进入特定学术项目
学生	参与学校教育活动，正在获取学位或证书的学习者
学籍注册	学生正式加入学校并被记录在特定学术项目中的过程
教学计划	学校为学生制定的课程和学习要求，指导他们完成学位的路径
学位	由学校颁发的证明学生已完成特定学术课程并达到要求的证书
进度跟踪	监控和记录学生在学术项目中完成课程和达到学习目标的过程"""
    user_story_model.ddd_model = """classDiagram
    class Faculty{
        - id: int
        - name: string
        - role: string
        + issueAdmissionNotice(student: Student, program: AcademicProgram)
    }

    class Student{
        - id: int
        - name: string
        - identityInfo: IdentityInfo
        + createAccount()
        + enroll(program: AcademicProgram, notice: AdmissionNotice)
        + checkProgress()
    }

    class AdmissionNotice{
        - id: int
        - program: AcademicProgram
        - issuedBy: Faculty
        + details(): string
    }

    class AcademicProgram{
        - id: int
        - name: string
        - requirements: Course[]
        + register(student: Student)
    }

    class Course{
        - id: int
        - name: string
        - credits: int
        + isCompleted(student: Student): bool
    }

    class ProgressTracking{
        - student: Student
        - program: AcademicProgram
        - completedCourses: Course[]
        + updateProgress()
        + viewProgress(): string
    }

    Faculty --> AdmissionNotice
    AdmissionNotice --> Student
    Student --> AcademicProgram
    AcademicProgram --> Course
    Student --> ProgressTracking
    ProgressTracking --> AcademicProgram
    ProgressTracking --> Course
"""
    return user_story_model.save()


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
