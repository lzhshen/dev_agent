from streamlit.logger import get_logger
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from streamlit_float import *

import database
from const import KEY_USER_STORY_ID
from models import UserStoryModel
from utils import *

ddd_model_template = """领域模型
======
```mermaid
{model}
```

用户故事
======
{story}

验收场景
======
{ac}

任务
===
数据都以yaml格式给出。
首先，请根据领域模型理解用户故事中的场景，并针对验收场景中Given的部分，给出样例数据。
然后，参看验收场景中When的部分，给出样例数据会产生怎样的改变。
"""

# app config
st.set_page_config(page_title="领域模型", page_icon="🤖", layout="wide")
st.title("领域模型")

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

    # ddd_glossary = st.text_area(
    #     label="DDD Glossary",
    #     value=user_story_model.ddd_glossary,
    #     # disabled=True,
    #     height=300,
    #     disabled=not user_story_id,
    #     placeholder="please input" if user_story_id else "need user story",
    #     # label_visibility="collapsed",
    # )

    acceptance_criteria = st.text_area(
        "Acceptance Criteria",
        value=user_story_model.acceptance_criteria,
        key="acceptance_criteria_content",
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
    )
    # ac_warning_container = st.empty()
    # if acceptance_criteria != user_story_model.acceptance_criteria:
    #     ac_warning_container.warning('unsaved', icon="ℹ")

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
                    template=ddd_model_template,
                    is_interactive=is_interactive,
                    input=user_query,
                    story=user_story,
                    context=business_ctx,
                    model=ddd_model,
                    glossary=acceptance_criteria,
                    ac=user_story_model.acceptance_criteria,
                ))
            st.session_state[KEY_CHAT_HISTORY].append(AIMessage(content=response))
