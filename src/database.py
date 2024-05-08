import functools
from sqlalchemy import create_engine, func, select, Engine
from sqlalchemy.orm import Session, sessionmaker
from models import BaseModel, BusinessContextModel, UserStoryModel, AcceptanceCriteriaModel


@functools.lru_cache()
def get_database_engine(url: str, reset_table: bool) -> Engine:
    engine = create_engine(url, echo=False)
    init_database_table(engine, reset_table)
    return engine


def init_database_table(engine: Engine, reset_table: bool):
    if reset_table:
        BaseModel.metadata.drop_all(bind=engine)
    BaseModel.metadata.create_all(bind=engine)


def get_database_session(config: dict) -> Session:
    url = config["url"]
    reset_table = config["reset_table"]
    engine = get_database_engine(url, reset_table)
    sess = sessionmaker(bind=engine)
    session = sess()
    return session


def clear_table(session: Session) -> str:
    success = "rollback"
    session.query(BusinessContextModel).delete()
    session.query(UserStoryModel).delete()
    session.query(AcceptanceCriteriaModel).delete()
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
    else:
        success = "commit"
    return success


def get_single_business_context(session: Session, id_: int):
    business_context = session.get(BusinessContextModel, id_)
    return business_context


def generate_fake_business_context(session: Session) -> str:
    success = "rollback"
    user_story = BusinessContextModel(
        title=f"业务背景",
        content="整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；",
    )
    session.add(user_story)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
    else:
        success = "commit"
    return success


def get_all_user_stories(session: Session):
    user_stories = session.query(UserStoryModel).all()
    return user_stories


def get_all_user_stories_sorted_desc(session: Session, by: str = "created"):
    user_stories = session.query(UserStoryModel).order_by(getattr(UserStoryModel, by).desc()).all()
    return user_stories


def get_all_user_stories_sorted_asc(session: Session, by: str = "created"):
    user_stories = session.query(UserStoryModel).order_by(getattr(UserStoryModel, by).asc()).all()
    return user_stories


def get_single_user_story(session: Session, id_: int):
    user_story = session.get(UserStoryModel, id_)
    return user_story


def generate_fake_user_story(session: Session, business_context_id) -> str:
    success = "rollback"
    user_story = UserStoryModel(
        business_context_id=business_context_id,
        title=f"获取学位的进度",
        content="""作为学校的教职员工（As a faculty），
我希望学生可以根据录取通知将学籍注册到教学计划上（I want the student to be able to enroll in an academic program with given offer），
从而我可以跟踪他们的获取学位的进度（So that I can track their progress）""",
    )
    session.add(user_story)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
    else:
        success = "commit"
    return success


def delete_user_story(session: Session, id_: int = None) -> str:
    success = "rollback"
    if id_:
        session.query(UserStoryModel).filter(UserStoryModel.id == id_).delete()
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        else:
            success = "commit"
    return success


def get_oldest_user_story(session: Session):
    user_story = session.query(UserStoryModel).order_by(UserStoryModel.created.asc()).first()
    return user_story


def get_newest_user_story(session: Session):
    user_story = session.query(UserStoryModel).order_by(UserStoryModel.created.desc()).first()
    return user_story


def get_random_user_story(session: Session):
    user_story = session.query(UserStoryModel).order_by(func.random()).first()
    return user_story


def get_user_story_count(session: Session):
    count = session.scalar(select(func.count(UserStoryModel.id)))
    return count


def test(config=None):
    if config is None:
        config = {"url": "sqlite:///sqlite.db", "reset_table": True}
    session = get_database_session(config)
    # init_database_table()
    # clear_table(session)
    generate_fake_business_context(session)
    business_context_model = session.query(BusinessContextModel).first()
    print(f"{business_context_model.id=} {business_context_model.title=}")
    for _ in range(3):
        generate_fake_user_story(session, business_context_model.id)
    print(get_user_story_count(session))
    for user_story_model in get_all_user_stories(session):
        print(user_story_model.id, user_story_model.title)


if __name__ == "__main__":
    test()
