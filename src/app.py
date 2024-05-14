import os

import streamlit as st
from streamlit.logger import get_logger
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.llms import Tongyi
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from streamlit_float import *
from langchain.agents import create_tool_calling_agent
from langchain.agents import initialize_agent, load_tools

import database
import view
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

log = get_logger(__name__)
log.info("###################### st.rerun ######################")

float_init(theme=True, include_unstable_primary=False)

load_dotenv()

# `set_page_config()` must be called as the first Streamlit command in your script.
database.init_database()


def get_response(user_query, chat_history, user_story, business_ctx, is_interactive=True):
    if "DASHSCOPE_API_KEY" in os.environ:
        llm_chat = Tongyi
        llm_model_name = "qwen1.5-0.5b-chat"  # 通义千问1.5对外开源的0.5B规模参数量是经过人类指令对齐的chat模型
        # llm_model_name = "qwen1.5-110b-chat"  # 通义千问1.5对外开源的110B规模参数量是经过人类指令对齐的chat模型
        # llm_model_name = "baichuan-7b-v1"  # 由百川智能开发的一个开源的大规模预训练模型，70亿参数，支持中英双语，上下文窗口长度为4096。
        # llm_model_name = "baichuan2-13b-chat-v1"  # 由百川智能开发的一个开源的大规模预训练模型，130亿参数，支持中英双语，上下文窗口长度为4096。
        # llm_model_name = "llama3-8b-instruct"  # Llama3系列是Meta在2024年4月18日公开发布的大型语言模型（LLMs），llama3-8B拥有80亿参数，模型最大输入为6500，最大输出为1500，仅支持message格式，限时免费调用。
        # llm_model_name = "ziya-llama-13b-v1"  # 姜子牙通用大模型由IDEA研究院认知计算与自然语言研究中心主导开源，具备翻译、编程、文本分类、信息抽取、摘要、文案生成、常识问答和数学计算等能力。
        # llm_model_name = "chatyuan-large-v2"  # ChatYuan模型是由元语智能出品的大规模语言模型，它在灵积平台上的模型名称为"chatyuan-large-v2"。ChatYuan-large-v2是一个支持中英双语的功能型对话语言大模型，是继ChatYuan系列中ChatYuan-large-v1开源后的又一个开源模型。

    # elif "OPENAI_API_KEY" in os.environ:
    else:
        llm_chat = ChatOpenAI
        llm_model_name = "gpt-4-turbo-preview"

    if is_interactive:
        llm = llm_chat(temperature=0.0, model=llm_model_name, model_kwargs={"stop": "\nAnswer"})
    else:
        llm = llm_chat(temperature=0.0, model=llm_model_name)
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

left_column, right_column = st.columns(2)
with right_column:
    # tab_user_story, tab_ddd, tab_tdd = st.tabs(["User Story", "DDD", "TDD"])
    # with tab_user_story:
    user_story, business_ctx = view.user_story_tab()

with left_column:
    with st.container(border=border, height=1100):
        # conversation
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)

        # user input
        user_query = ''
        with st.container():
            is_interactive = st.checkbox("交互对话模式", value=False)

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

