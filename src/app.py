import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from streamlit_float import *
from langchain.agents import create_tool_calling_agent
from langchain.agents import initialize_agent, load_tools
from sqlalchemy import text
import database
import models
from utils import *

user_story_template = """
You are a business analyst who is familiar with specification by example. I’m the domain expert.
// 你是一个业务分析师，而我是领域专家 

===CONTEXT
{context}
===END OF CONTEXT

===USER STORY
{story}
===END OF USER STORY 

Explain the user story as scenarios. Use the following format:
// 使用 场景 解释用户故事，并遵循如下格式 

Thought: you should always think about what is still uncertain about the user story. Ignore technical concerns.
// 思考：你应该考虑用户故事中不清晰的部分。但忽略技术细节
Question: the question to ask to clarify the user story
// 问题：提出问题帮助你澄清这个用户故事
Answer: the answer I responded to the question
// 回答：我给出答案
… (this Thought/Question/Answer repeat at least 3 times, at most 10 times)
//（Thought/Question/Answer 重复至少 3 次而不多于 10 次）
Thought: I know enough to explain the user story
// 思考：我已经对这个用户故事了解了足够多的内容
Scenarios: List all possible scenarios with concrete example in Given/When/Then style
// 场景：列出所有场景。使用 Given/When/Then 的格式表述

对于每个步骤（Thought/Question/Answer/Scenarios）请换行输出其内容

{history}
{input}
请使用中文
"""
# app config
st.set_page_config(page_title="Streaming bot", page_icon="🤖", layout="wide")
st.title("Streaming bot")

float_init(theme=True, include_unstable_primary=False)

load_dotenv()


@st.cache_resource(ttl=3600, show_spinner=False)
def get_database_session():
    database_config = st.secrets["database"]
    return database.get_database_session(database_config)


if 'dbsession' not in st.session_state:
    st.session_state.dbsession = get_database_session()


def get_response(user_query, chat_history, user_story, business_ctx, is_interactive = True):
  
    if is_interactive:
        llm = ChatOpenAI(temperature=0.0, model="gpt-4-turbo-preview", model_kwargs={"stop": "\nAnswer"})
    else:
        llm = ChatOpenAI(temperature=0.0, model="gpt-4-turbo-preview")
    # output_parser = StrOutputParser()
    output_parser = MyStrOutputParser()
    prompt = ChatPromptTemplate.from_template(user_story_template)
    chain = prompt | llm | output_parser

    stream = chain.stream(
        {
            "input": user_query,
            "history": chat_history,
            "story": user_story,
            "context": business_ctx,
        }
    )
    return stream


# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    border = False
else:
    border = True

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]
    border = False
else:
    border = True


user_story_list: [models.UserStoryModel] = st.session_state.dbsession.query(
    models.UserStoryModel,
).filter(
    models.UserStoryModel.status == models.STATUS_ALIVE,
).order_by(
    models.UserStoryModel.created.desc()
).all()
user_story_selectbox_options = [user_story_model.id for user_story_model in user_story_list]
if "user_story_id" in st.session_state and st.session_state.user_story_id in user_story_selectbox_options:
    user_story_selectbox_index = user_story_selectbox_options.index(st.session_state.user_story_id)
else:
    user_story_selectbox_index = 0

business_ctx_list: [models.BusinessCtxModel] = st.session_state.dbsession.query(
    models.BusinessCtxModel
).filter(
    models.BusinessCtxModel.status == models.STATUS_ALIVE,
).order_by(
    models.BusinessCtxModel.created.desc()
).all()
business_ctx_selectbox_options = [business_ctx_model.id for business_ctx_model in business_ctx_list]
if "business_ctx_id" in st.session_state and st.session_state.business_ctx_id in business_ctx_selectbox_options:
    business_ctx_selectbox_index = business_ctx_selectbox_options.index(st.session_state.business_ctx_id)
    business_ctx_selectbox_id = st.session_state.business_ctx_id
elif business_ctx_selectbox_options:
    business_ctx_selectbox_index = 0
    business_ctx_selectbox_id = business_ctx_selectbox_options[business_ctx_selectbox_index]
    st.session_state.business_ctx_id = business_ctx_selectbox_id
else:
    business_ctx_selectbox_index = 0


def format_user_story_selectbox(user_story_id):
    user_story_model: models.UserStoryModel = st.session_state.dbsession.get(
        models.UserStoryModel,
        user_story_id,
    )
    if user_story_model:
        user_story_title = user_story_model.title
    else:
        user_story_title = f"用户故事已被删除，ID={user_story_model}"
    return user_story_title


def format_user_story_text_area(user_story_id):
    if user_story_id is None:
        return ""
    user_story_model: models.UserStoryModel = st.session_state.dbsession.get(
        models.UserStoryModel,
        user_story_id,
    )
    if user_story_model:
        user_story_content = user_story_model.content
    else:
        user_story_content = f"用户故事已被删除，ID={user_story_model}"
    return user_story_content


def format_business_ctx_selectbox(business_ctx_id):
    business_ctx_model: models.BusinessCtxModel = st.session_state.dbsession.get(
        models.BusinessCtxModel,
        business_ctx_id,
    )
    if business_ctx_model:
        business_ctx_title = business_ctx_model.title
    else:
        business_ctx_title = f"业务背景已被删除，ID={business_ctx_model}"
    return business_ctx_title


def format_business_ctx_text_area(business_ctx_id):
    if business_ctx_id is None:
        return ""
    business_ctx_model: models.BusinessCtxModel = st.session_state.dbsession.get(
        models.BusinessCtxModel,
        business_ctx_id,
    )
    if business_ctx_model:
        business_ctx_content = business_ctx_model.content
    else:
        business_ctx_content = f"业务背景已被删除，ID={business_ctx_model}"
    return business_ctx_content


def on_change_user_story_content():
    user_story_id = st.session_state.user_story_id
    user_story_content = st.session_state.user_story_content
    if user_story_id is None:
        # dialog_add_user_story(user_story_content)  # RuntimeError: Could not find fragment with id
        return
    user_story_model: models.UserStoryModel = st.session_state.dbsession.get(
        models.UserStoryModel,
        user_story_id,
    )
    user_story_model.content = user_story_content
    st.session_state.dbsession.commit()


def on_change_user_business_ctx():
    business_ctx_id = st.session_state.business_ctx_id
    business_ctx_content = st.session_state.business_ctx_content
    if business_ctx_id:
        business_ctx_model: models.BusinessCtxModel = st.session_state.dbsession.get(
            models.BusinessCtxModel,
            business_ctx_id,
        )
        if business_ctx_model:
            business_ctx_model.content = business_ctx_content
    else:
        business_ctx_model: models.BusinessCtxModel = models.BusinessCtxModel(
            content=business_ctx_content,
        )
        st.session_state.dbsession.add(business_ctx_model)
        st.session_state.business_ctx_id = business_ctx_model.id
    st.session_state.dbsession.commit()


@st.experimental_dialog("new user story")
def dialog_add_user_story(content=""):
    user_story_title = st.text_input("title")
    if st.button("Submit"):
        user_story_model = models.UserStoryModel(
            business_ctx_id=st.session_state.business_ctx_id,
            title=user_story_title,
            content=content,
        )
        st.session_state.dbsession.add(user_story_model)
        st.session_state.dbsession.commit()
        st.session_state.user_story_id = user_story_model.id
        st.rerun()


@st.experimental_dialog("modify user story title")
def dialog_modify_user_story_title():
    user_story_title = st.text_input("title", format_user_story_selectbox(st.session_state.user_story_id))
    if st.button("Submit"):
        user_story_model = st.session_state.dbsession.get(
            models.UserStoryModel,
            st.session_state.user_story_id,
        )
        user_story_model.title = user_story_title
        st.session_state.dbsession.commit()
        st.rerun()


@st.experimental_dialog("delete user story")
def dialog_delete_user_story():
    dialog_left_column, dialog_right_column = st.columns(2)
    confirm = dialog_left_column.button("Confirm", type="primary")
    dialog_right_column.button("Cancel")
    if confirm:
        user_story_model: models.UserStoryModel = st.session_state.dbsession.get(
            models.UserStoryModel,
            st.session_state.user_story_id,
        )
        user_story_model.status = models.STATUS_DELETE
        st.session_state.dbsession.commit()
        st.rerun()


left_column, right_column = st.columns(2)
with right_column:
    left_column2, right_column2 = st.columns([0.9, 0.1])

    with left_column2:
        user_story_selectbox_id = st.selectbox(
          "User Story List",
          options=user_story_selectbox_options,
          key="user_story_id",
          format_func=format_user_story_selectbox,
          index=user_story_selectbox_index,
        )

    with right_column2:
        container = st.container(height=12, border=False)
        with st.popover(
                label="操作",
                use_container_width=True,  # 宽度适配父容器
        ):
            button_add_clicked = st.button(
                "添加",
                disabled=not st.session_state.get("business_ctx_id"),
                help="请先添加"
            )
            button_modify_clicked = st.button(
                "修改",
                disabled=not user_story_selectbox_options,
            )
            button_delete_clicked = st.button(
                "删除",
                disabled=not user_story_selectbox_options,
                type="primary",
            )

        if button_add_clicked:
            dialog_add_user_story()
        if button_modify_clicked:
            dialog_modify_user_story_title()
        if button_delete_clicked:
            dialog_delete_user_story()

    if st.session_state.user_story_id:
        user_story = st.text_area(
            "User Story",
            format_user_story_text_area(user_story_selectbox_id),
            key="user_story_content",
            height=300,
            on_change=on_change_user_story_content,
        )
    else:
        user_story = st.text_area(
            "User Story",
            # disabled=True,
            key="user_story_content",
            height=300,
            # on_change=on_change_user_story_content,
        )
        if user_story:
            dialog_add_user_story(user_story)

    # TODO st.selectbox ac
    # TODO st.text_area ac

    # TODO st.selectbox business_ctx

    business_ctx = st.text_area(
        "Business Context",
        format_business_ctx_text_area(business_ctx_selectbox_id),
        key="business_ctx_content",
        height=300,
        on_change=on_change_user_business_ctx,
    )

with left_column:    
    with st.container(border=border, height=800):
        # conversation
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)

        # user input
        is_interactive = st.checkbox("交互对话模式", value=True)
        user_query = ''
        with st.container():
            user_query = st.chat_input("What is up?")
            button_b_pos = "0rem"
            button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            float_parent(css=button_css)

        if user_query is not None and user_query != "":
            st.session_state.chat_history.append(HumanMessage(content=user_query))

            with st.chat_message("Human"):
                st.markdown(user_query)

            with st.chat_message("AI"):
                # response = st.write_stream(get_response(user_query, st.session_state.chat_history, right_column.user_story, right_column.business_ctx))
                response = st.write_stream(get_response(user_query, st.session_state.chat_history, user_story, business_ctx, is_interactive))

            st.session_state.chat_history.append(AIMessage(content=response))

