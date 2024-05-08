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

# 新增用户故事-特殊ID
NEW_USER_STORY_ID = -1

# app config
st.set_page_config(page_title="Streaming bot", page_icon="🤖", layout="wide")
st.title("Streaming bot")

float_init(theme=True, include_unstable_primary=False)

load_dotenv()


@st.cache_resource(ttl=3600, show_spinner=False)
def get_database_session():
    database_config = st.secrets["database"]
    return database.get_database_session(database_config)


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


if 'dbsession' not in st.session_state:
    st.session_state.dbsession = get_database_session()
    database.test()

user_story_list = database.get_all_user_stories(st.session_state.dbsession)
print(user_story_list)
user_story_selectbox_options = [user_story_model.id for user_story_model in user_story_list]
user_story_selectbox_options.insert(0, NEW_USER_STORY_ID)
if "user_story_id" in st.session_state and st.session_state.user_story_id in user_story_selectbox_options:
    user_story_selectbox_index = user_story_selectbox_options.index(st.session_state.user_story_id)
else:
    user_story_selectbox_index = len(user_story_selectbox_options) - 1


def format_user_story_selectbox(user_story_id):
    if user_story_id == NEW_USER_STORY_ID:
        return "新增用户故事"
    else:
        for user_story_model in user_story_list:
            if user_story_model.id == user_story_id:
                return user_story_model.title
    return f"用户故事已被删除，ID={user_story_id}"


def format_user_story_text_area(user_story_id):
    if user_story_id == NEW_USER_STORY_ID:
        return ""
    else:
        for user_story_model in user_story_list:
            if user_story_model.id == user_story_id:
                return user_story_model.content
    return f"用户故事已被删除，ID={user_story_id}"


def on_change_user_story_content():
    user_story_id = st.session_state.user_story_id
    user_story_content = st.session_state.user_story_content
    if user_story_id == NEW_USER_STORY_ID:
        sql = "INSERT INTO user_story_list (user_story_content) VALUES (:user_story_content);"
        params = {
            "user_story_content": user_story_content,
        }
        del st.session_state["user_story_id"]
    else:
        sql = "UPDATE user_story_list SET user_story_content=:user_story_content WHERE user_story_id=:user_story_id;"
        params = {
            "user_story_content": user_story_content,
            "user_story_id": user_story_id,
        }
    with conn.session as conn_session:
        conn_session.execute(
            statement=text(sql),
            params=params,
        )
        conn_session.commit()


left_column, right_column = st.columns(2)
with right_column:
    user_story_selectbox_index = st.selectbox(
      "User Story List",
      options=user_story_selectbox_options,
      key="user_story_id",
      format_func=format_user_story_selectbox,
      index=user_story_selectbox_index,
    )

    user_story = st.text_area(
        "User Story",
        format_user_story_text_area(user_story_selectbox_index),
        key="user_story_content",
        height= 300,
        on_change=on_change_user_story_content
    )

    business_ctx = st.text_area(
        "Business Context",
        "整个学籍管理系统是一个 Web 应用； 当教职员工发放录取通知时，会同步建立学生的账号；学生可以根据身份信息，查询自己的账号；在报道注册时，学生登录账号，按照录取通知书完成学年的注册；",
        height= 300,
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

