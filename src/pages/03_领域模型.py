import os.path

from streamlit.logger import get_logger
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from streamlit_float import *

import database
from const import KEY_USER_STORY_ID
from models import UserStoryModel
from utils import *

ddd_model_template = """业务描述
=======
{context}

用户故事
======
{story}

领域模型
======
```mermaid
{model}
```

======

系统中涉及概念的glossary如下：
{glossary}

任务
====
根据业务描述，为系统建立模型。可以添加你认为必要的实体和关系。并将模型表示为mermaid的class diagram
"""

# app config
st.set_page_config(page_title="领域模型", page_icon="🤖", layout="wide")
st.title("领域模型")

log = get_logger(__name__)
file_name = os.path.basename(__file__)
log.info(f"###################### st.rerun {file_name} start ######################")

float_init(theme=True, include_unstable_primary=False)

load_dotenv()

# `set_page_config()` must be called as the first Streamlit command in your script.
database.init_database()


left_column, right_column = st.columns(2)
with right_column:
    user_story_model_list: List[UserStoryModel] = UserStoryModel.list()
    user_story_selectbox_options = [user_story_model.id for user_story_model in user_story_model_list]
    if "selectbox_user_story_id" in st.session_state and \
            st.session_state["selectbox_user_story_id"] in user_story_selectbox_options:
        user_story_id = st.session_state["selectbox_user_story_id"]
        user_story_selectbox_index = user_story_selectbox_options.index(user_story_id)
    elif KEY_USER_STORY_ID in st.session_state and st.session_state[KEY_USER_STORY_ID] in user_story_selectbox_options:
        user_story_id = st.session_state[KEY_USER_STORY_ID]
        user_story_selectbox_index = user_story_selectbox_options.index(user_story_id)
    elif user_story_selectbox_options:
        user_story_selectbox_index = 0
        user_story_id = user_story_selectbox_options[0]
    else:
        user_story_selectbox_index = 0
        user_story_id = None
    log.debug(f"{user_story_selectbox_index=} {user_story_id=}")

    user_story_id = st.selectbox(
        label="User Story List",
        options=user_story_selectbox_options,
        key="selectbox_user_story_id",  # Warning: st.session_state reset when switch page
        # format_func=lambda id_: UserStoryModel.get(id_).title,
        format_func=lambda id_: UserStoryModel.get(id_).title,
        index=user_story_selectbox_index,
        # on_change=on_change_user_story_list(),
        # help=format_user_story_text_area(user_story_id),
    )
    st.session_state[KEY_USER_STORY_ID] = user_story_id
    user_story_model = UserStoryModel.get_or_create(user_story_id)

    ddd_model = st.text_area(
        label="DDD Model",
        value=user_story_model.ddd_model,
        # disabled=True,
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
        # label_visibility="collapsed",
    )
    empty_warning = st.empty()
    if ddd_model != user_story_model.ddd_model:
        empty_warning.warning('unsaved', icon="ℹ")

    button_save_ddd_model_clicked = st.button(
        "保存",
        key="button_save_ddd_model",
        disabled=not user_story_id,
    )
    if button_save_ddd_model_clicked:
        user_story_model.ddd_model = ddd_model
        user_story_model.save()
        empty_warning.info('save success', icon="🎉")
        # empty_warning.empty()
        # st.toast('save success', icon='🎉')

    if ddd_model and st.secrets.get("mermaid_ddd_model"):
        show_diagram(ddd_model)
        # import streamlit_mermaid as stmd
        # import streamlit as st
        #
        # format_ddd_model = re.sub(r"list<(.+?)>", r"list~\1~", ddd_model)
        # mermaid = stmd.st_mermaid(format_ddd_model)
        # st.write(mermaid)

    ddd_glossary = st.text_area(
        label="DDD Glossary",
        value=user_story_model.ddd_glossary,
        # disabled=True,
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
        # label_visibility="collapsed",
    )

    user_story = st.text_area(
        "User Story",
        user_story_model.content,
        # disabled=True,
        key="user_story_content",
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need add user story",
        # label_visibility="collapsed",
    )

    business_ctx = st.text_area(
        "Business Context",
        value=user_story_model.business_ctx,
        key="business_ctx_content",
        height=300,
        # on_change=on_change_user_business_ctx,
    )
    # bc_warning_container = st.empty()
    # if business_ctx != user_story_model.business_ctx:
    #     bc_warning_container.warning('unsaved', icon="ℹ")
    # button_save_business_ctx_clicked = st.button("保存", key="button_save_business_ctx")
    # if button_save_business_ctx_clicked:
    #     # TODO
    #     for model in UserStoryModel.list():
    #         model.business_ctx = business_ctx
    #         model.save()
    #     bc_warning_container.info('save success', icon="🎉")

with left_column:
    # Initialize chat history
    file_name = os.path.basename(__file__)
    KEY_CHAT_HISTORY = f"KEY_CHAT_HISTORY_{file_name}_{user_story_id}"
    if KEY_CHAT_HISTORY not in st.session_state:
        st.session_state[KEY_CHAT_HISTORY] = []
    border = True

    with st.container(border=border, height=1100):
        KEY_CHAT_INIT = f"KEY_CHAT_INIT_{file_name}"
        if not st.session_state.get(KEY_CHAT_INIT):
            st.session_state[KEY_CHAT_INIT] = True
            system_message = SystemMessage(content=ddd_model_template)
            # with st.chat_message(system_message.type):
            #     st.text(system_message.content)
            st.session_state[KEY_CHAT_HISTORY].append(system_message)

        # conversation
        for message in st.session_state[KEY_CHAT_HISTORY]:
            # if isinstance(message, AIMessage):
            #     with st.chat_message("AI"):
            #         st.write(message.content)
            # elif isinstance(message, HumanMessage):
            #     with st.chat_message("Human"):
            #         st.write(message.content)
            with st.chat_message(message.type):
                if isinstance(message, AIMessage):
                    st.write(message.content)
                else:
                    st.text(message.content)

        # user input
        # user_query = ''
        with st.container():
            is_interactive = st.checkbox("交互对话模式", value=False)

            user_query = st.chat_input("What is up?")
            button_b_pos = "0rem"
            button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            float_parent(css=button_css)

        if user_query is not None and user_query != "":
            if not is_interactive:
                user_query = ddd_model_template.format(
                    input=user_query,
                    story=user_story,
                    context=business_ctx,
                    model=ddd_model,
                    glossary=ddd_glossary,
                )
            st.session_state[KEY_CHAT_HISTORY].append(HumanMessage(content=user_query))

            with st.chat_message("Human"):
                st.text(user_query)

            with st.chat_message("AI"):
                response = st.write_stream(get_response(
                    template=ddd_model_template,
                    is_interactive=is_interactive,
                    input=user_query,
                    story=user_story,
                    context=business_ctx,
                    model=ddd_model,
                    glossary=ddd_glossary,
                ))
            st.session_state[KEY_CHAT_HISTORY].append(AIMessage(content=response))

log.info(f"###################### st.rerun {file_name} end ######################")
