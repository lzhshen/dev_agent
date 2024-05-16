import os

from streamlit.logger import get_logger
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from streamlit_float import *

import database
from models import (
    AcceptanceCriteriaModel,
    BusinessCtxModel,
    UserStoryModel,
)
from utils import *

ddd_dict_template = """用户故事
======
{story}

任务
===
请根据用户故事中描述的业务场景，提取其中的业务概念，并给出每个概念的定义。
结果以表格形式给出。
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


# Initialize chat history
if "ddd_chat_history" not in st.session_state:
    st.session_state.ddd_chat_history = []
    border = False
else:
    border = True


left_column, right_column = st.columns(2)
with right_column:

    business_ctx_list: [BusinessCtxModel] = BusinessCtxModel.list()
    business_ctx_selectbox_options = [business_ctx_model.id for business_ctx_model in business_ctx_list]
    if "business_ctx_id" in st.session_state and st.session_state.business_ctx_id in business_ctx_selectbox_options:
        # business_ctx_selectbox_index = business_ctx_selectbox_options.index(st.session_state.business_ctx_id)
        business_ctx_id = st.session_state.business_ctx_id
    elif business_ctx_selectbox_options:
        # business_ctx_selectbox_index = 0
        business_ctx_id = business_ctx_selectbox_options[0]
        st.session_state.business_ctx_id = business_ctx_id
    else:
        # business_ctx_selectbox_index = 0
        business_ctx_id = None
        st.session_state.business_ctx_id = None
    log.debug(f"{business_ctx_id=} {st.session_state.business_ctx_id=}")

    user_story_list: [UserStoryModel] = UserStoryModel.list(
        UserStoryModel.business_ctx_id == business_ctx_id
    )
    user_story_selectbox_options = [user_story_model.id for user_story_model in user_story_list]
    if "user_story_id" in st.session_state and st.session_state.user_story_id in user_story_selectbox_options:
        user_story_selectbox_index = user_story_selectbox_options.index(st.session_state.user_story_id)
        user_story_id = st.session_state["user_story_id"]
    elif user_story_selectbox_options:
        user_story_selectbox_index = 0
        user_story_id = user_story_selectbox_options[user_story_selectbox_index]
        st.session_state.user_story_id = user_story_id
    else:
        user_story_selectbox_index = 0
        user_story_id = None
        st.session_state.user_story_id = None
    log.debug(f"{user_story_selectbox_index=} {user_story_id=} {st.session_state.user_story_id=}")

    acceptance_criteria_list: [AcceptanceCriteriaModel] = AcceptanceCriteriaModel.list(
        AcceptanceCriteriaModel.user_story_id == user_story_id,
    )
    acceptance_criteria_selectbox_options = [
        acceptance_criteria_model.id for acceptance_criteria_model in acceptance_criteria_list
    ]
    if "acceptance_criteria_id" in st.session_state and \
            st.session_state.acceptance_criteria_id in acceptance_criteria_selectbox_options:
        # acceptance_criteria_selectbox_index = acceptance_criteria_selectbox_options.index(
        #     st.session_state.acceptance_criteria_id
        # )
        acceptance_criteria_id = st.session_state.acceptance_criteria_id
    elif acceptance_criteria_selectbox_options:
        # acceptance_criteria_selectbox_index = 0
        acceptance_criteria_id = acceptance_criteria_selectbox_options[0]
        st.session_state.acceptance_criteria_id = acceptance_criteria_id
    else:
        # acceptance_criteria_selectbox_index = None
        acceptance_criteria_id = None
        st.session_state.acceptance_criteria_id = None
    log.debug(f"{acceptance_criteria_id=} {st.session_state.acceptance_criteria_id=}")

    # streamlit elements function
    def format_user_story_selectbox(format_user_story_id):
        user_story_model: UserStoryModel = UserStoryModel.get(
            format_user_story_id,
        )
        if user_story_model:
            user_story_title = user_story_model.title
        else:
            user_story_title = f"用户故事已被删除，ID={user_story_model}"
        return user_story_title

    def format_user_story_text_area(format_user_story_id):
        if format_user_story_id is None:
            return ""
        user_story_model = UserStoryModel.get(
            format_user_story_id,
        )
        if user_story_model:
            user_story_content = user_story_model.content
        else:
            user_story_content = f"用户故事已被删除，ID={user_story_model}"
        return user_story_content

    user_story_id = st.selectbox(
        "User Story List",
        options=user_story_selectbox_options,
        key="user_story_id",
        format_func=format_user_story_selectbox,
        index=user_story_selectbox_index,
        # on_change=on_change_user_story_list(),
        # help=format_user_story_text_area(user_story_id),
    )

    if user_story_id:
        text_area_value = format_user_story_text_area(user_story_id)
    else:
        text_area_value = ""

    ddd_dict = st.text_area(
        "DDD Dict",
        "",
        # disabled=True,
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
        # label_visibility="collapsed",
    )
    button_save_ddd_dict_clicked = st.button("保存", key="button_save_ddd_dict")

    user_story = st.text_area(
        "User Story",
        text_area_value,
        # disabled=True,
        key="user_story_content",
        height=300,
        disabled=not business_ctx_id,
        placeholder="please input" if business_ctx_id else "need business ctx",
        # label_visibility="collapsed",
    )
    # st.text(
    #     text_area_value
    # )


with left_column:
    with st.container(border=border, height=1100):
        # conversation
        for message in st.session_state.ddd_chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)

        # user input
        # user_query = ''
        with st.container():
            is_interactive = st.checkbox("交互对话模式", value=False)

            user_query = st.chat_input("What is up?")
            button_b_pos = "0rem"
            button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            float_parent(css=button_css)

        if user_query is not None and user_query != "":
            st.session_state.ddd_chat_history.append(HumanMessage(content=user_query))

            with st.chat_message("Human"):
                st.markdown(user_query)

            with st.chat_message("AI"):
                response = st.write_stream(get_response(
                    template=ddd_dict_template,
                    is_interactive=is_interactive,
                    input=user_query,
                    story=user_story,
                ))
            st.session_state.ddd_chat_history.append(AIMessage(content=response))
