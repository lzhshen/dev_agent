from streamlit.logger import get_logger
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from streamlit_float import *

import database
from models import UserStoryModel
from const import KEY_USER_STORY_ID
from utils import *

user_story_template = """You are a business analyst who is familiar with specification by example. I’m the domain expert.
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

    # if user_story_selectbox_options:
    #     user_story_model = user_story_model_list[user_story_selectbox_index]
    # else:
    #     user_story_model = UserStoryModel()
    #
    log.debug(f"{user_story_selectbox_index=} {user_story_id=}")

    def on_change_user_story_list():
        global user_story_id, user_story_model
        log.debug(f"on change user_story_id={user_story_id} session={st.session_state.get(KEY_USER_STORY_ID)} "
                  f"select={st.session_state.get('selectbox_user_story_id')}")
        # user_story_id = st.session_state.get('selectbox_user_story_id')
        # user_story_model = UserStoryModel.get_or_create(user_story_id)
        # st.session_state[KEY_USER_STORY_ID] = st.session_state.get('selectbox_user_story_id')

    log.debug(f"before user_story_id={user_story_id} session={st.session_state.get(KEY_USER_STORY_ID)} "
              f"select={st.session_state.get('selectbox_user_story_id')}")

    user_story_id = st.selectbox(
        label="User Story List",
        options=user_story_selectbox_options,
        key="selectbox_user_story_id",  # Warning: st.session_state reset when switch page
        format_func=lambda id_: UserStoryModel.get(id_).title,
        index=user_story_selectbox_index,
        # on_change=on_change_user_story_list(),
        # help=format_user_story_text_area(user_story_id),
    )
    st.session_state[KEY_USER_STORY_ID] = st.session_state.get('selectbox_user_story_id')
    user_story_model = UserStoryModel.get_or_create(user_story_id)
    log.debug(f"{user_story_model.id=} {user_story_model.title}")
    log.debug(f"after user_story_id={user_story_id} session={st.session_state.get(KEY_USER_STORY_ID)} "
              f"select={st.session_state.get('selectbox_user_story_id')}")

    user_story = st.text_area(
        "User Story",
        user_story_model.content,
        # disabled=True,
        key="user_story_content",
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need add user story",
        # label_visibility="collapsed",
    )
    us_warning_container = st.empty()
    if user_story != user_story_model.content:
        us_warning_container.warning('unsaved', icon="ℹ")

    (
        right_column_us_save,
        right_column_us_add,
        right_column_us_delete,
        left_column_us_info,
        left_column_ac_info,
    ) = st.columns([1, 1, 1, 3, 3])

    with right_column_us_add:
        button_add_clicked = st.button(
            "新增",
        )
    with right_column_us_save:
        button_save_clicked = st.button(
            "保存",
            key="button_save",
            disabled=not user_story_id,
        )
    with right_column_us_delete:
        button_delete_clicked = st.button(
            "删除",
            key="button_delete_clicked",
            disabled=not user_story_id,
            type="primary",
        )

    acceptance_criteria = st.text_area(
        "Acceptance Criteria",
        value=user_story_model.acceptance_criteria,
        key="acceptance_criteria_content",
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
    )
    ac_warning_container = st.empty()
    if acceptance_criteria != user_story_model.acceptance_criteria:
        ac_warning_container.warning('unsaved', icon="ℹ")

    business_ctx = st.text_area(
        "Business Context",
        value=user_story_model.business_ctx,
        key="business_ctx_content",
        height=300,
        # on_change=on_change_user_business_ctx,
    )
    bc_warning_container = st.empty()
    if business_ctx != user_story_model.business_ctx:
        bc_warning_container.warning('unsaved', icon="ℹ")
    button_save_business_ctx_clicked = st.button("保存", key="button_save_business_ctx")

    # function
    @st.experimental_dialog("new user story")
    def dialog_add_user_story(content=""):
        user_story_title = st.text_input("title")
        if st.button("Submit"):
            new_user_story_model = UserStoryModel(
                title=user_story_title,
                content=content,
                business_ctx=user_story_model.business_ctx,
            ).save()
            st.session_state["selectbox_user_story_id"] = new_user_story_model.id
            # st.session_state[KEY_USER_STORY_ID] = new_user_story_model.id
            st.rerun()

    @st.experimental_dialog(f"delete user story")
    def dialog_delete_user_story():
        del_model = UserStoryModel.get(user_story_id)
        st.write(f"delete {del_model.title}")
        dialog_left_column, dialog_right_column = st.columns(2)
        if dialog_left_column.button("Confirm", type="primary"):
            del_model.delete()
            del st.session_state[KEY_USER_STORY_ID]
            st.rerun()
        if dialog_right_column.button("Cancel"):
            st.rerun()

    if button_add_clicked:
        dialog_add_user_story()
    if button_save_clicked:
        user_story_model.content = user_story
        user_story_model.acceptance_criteria = acceptance_criteria
        user_story_model.save()
        us_warning_container.info('save success', icon="🎉")
        ac_warning_container.info('save success', icon="🎉")
        # us_warning_container.empty()
        # st.toast('save success', icon='🎉')
    if button_delete_clicked:
        dialog_delete_user_story()
    if button_save_business_ctx_clicked:
        # TODO
        for model in UserStoryModel.list():
            model.business_ctx = business_ctx
            model.save()
        bc_warning_container.info('save success', icon="🎉")


with left_column:
    # Initialize chat history
    KEY_CHAT_HISTORY = f"KEY_CHAT_HISTORY_{file_name}_{user_story_id}"
    if KEY_CHAT_HISTORY not in st.session_state:
        st.session_state[KEY_CHAT_HISTORY] = []
    border = True

    with st.container(border=border, height=1100):
        KEY_CHAT_INIT = f"KEY_CHAT_INIT_{file_name}"
        if not st.session_state.get(KEY_CHAT_INIT):
            st.session_state[KEY_CHAT_INIT] = True
            system_message = SystemMessage(content=user_story_template)
            # with st.chat_message(system_message.type):
            #     st.write(system_message.content)
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
                if message.type.lower() == "ai":
                    st.write(message.content)
                else:
                    st.text(message.content)

        # user input
        with st.container():
            is_interactive = st.checkbox("交互对话模式", value=False)

            # st.selectbox(
            #     "大模型",
            #     options=[
            #         "",
            #         "qwen1.5-0.5b-chat",
            #         "qwen1.5-110b-chat",
            #         "baichuan-7b-v1",
            #         "baichuan2-13b-chat-v1",
            #         "llama3-8b-instruct",
            #         "ziya-llama-13b-v1",
            #         "chatyuan-large-v2",
            #     ],
            #     key="llm_model_name",
            #     index=0,
            # )

            user_query = st.chat_input("What is up?")
            button_b_pos = "0rem"
            button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            float_parent(css=button_css)

        # if user_query is not None and user_query != "" and st.session_state.llm_model_name:
        if user_query is not None and user_query != "":
            if not is_interactive:
                user_query = user_story_template.format(
                    template=user_story_template,
                    input=user_query,
                    history="",  # st.session_state[KEY_CHAT_HISTORY],
                    story=user_story,
                    context=business_ctx,
                    is_interactive=is_interactive,
                )
            st.session_state[KEY_CHAT_HISTORY].append(HumanMessage(content=user_query))

            with st.chat_message("Human"):
                st.text(user_query)

            with st.chat_message("AI"):
                response = st.write_stream(get_response(
                    template=user_story_template,
                    input=user_query,
                    history=st.session_state[KEY_CHAT_HISTORY] if st.session_state[KEY_CHAT_HISTORY] else "",
                    story=user_story,
                    context=business_ctx,
                    is_interactive=is_interactive,
                ))

            st.session_state[KEY_CHAT_HISTORY].append(AIMessage(content=response))

log.info(f"###################### st.rerun {file_name} end ######################")
