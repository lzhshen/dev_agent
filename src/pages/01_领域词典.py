from streamlit.logger import get_logger
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from streamlit_float import *

import database
from const import KEY_USER_STORY_ID
from models import UserStoryModel
from utils import *

ddd_glossary_template = """用户故事
======
{story}

任务
===
请根据用户故事中描述的业务场景，提取其中的业务概念，并给出每个概念的定义。
结果以表格形式给出。
"""

# app config
st.set_page_config(page_title="领域词典", page_icon="🤖", layout="wide")
st.title("领域词典")

log = get_logger(__name__)
log.info("###################### st.rerun ######################")

float_init(theme=True, include_unstable_primary=False)

load_dotenv()

# `set_page_config()` must be called as the first Streamlit command in your script.
database.init_database()


# Initialize chat history
file_name = os.path.basename(__file__)
KEY_CHAT_HISTORY = f"KEY_CHAT_HISTORY_{file_name}"
if KEY_CHAT_HISTORY not in st.session_state:
    st.session_state[KEY_CHAT_HISTORY] = []
    border = False
else:
    border = True

# session state
if KEY_CHAT_HISTORY not in st.session_state:
    st.session_state[KEY_CHAT_HISTORY] = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]
    border = False
else:
    border = True

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

    ddd_glossary = st.text_area(
        label="DDD Glossary",
        value=user_story_model.ddd_glossary,
        # disabled=True,
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
        # label_visibility="collapsed",
    )
    empty_warning = st.empty()
    if ddd_glossary != user_story_model.ddd_glossary:
        empty_warning.warning('unsaved', icon="ℹ")

    button_save_ddd_glossary_clicked = st.button(
        "保存",
        key="button_save_ddd_glossary",
        disabled=not user_story_id,
    )
    if button_save_ddd_glossary_clicked:
        user_story_model.ddd_glossary = ddd_glossary
        user_story_model.save()
        empty_warning.info('save success', icon="🎉")
        # empty_warning.empty()
        # st.toast('save success', icon='🎉')

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


with left_column:
    with st.container(border=border, height=1100):
        # conversation
        for message in st.session_state[KEY_CHAT_HISTORY]:
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
            st.session_state[KEY_CHAT_HISTORY].append(HumanMessage(content=user_query))

            with st.chat_message("Human"):
                st.markdown(user_query)

            with st.chat_message("AI"):
                response = st.write_stream(get_response(
                    template=ddd_glossary_template,
                    is_interactive=is_interactive,
                    input=user_query,
                    story=user_story,
                ))
            st.session_state[KEY_CHAT_HISTORY].append(AIMessage(content=response))
