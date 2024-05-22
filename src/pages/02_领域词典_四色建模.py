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

概念提取的方法
============
在使用四色法建模时，我们将使用 4 个基本原型（Archetype）：'Moment-interval'、'role'、'party-place-thing' 和 'description'。
在这四个原型中，最重要的原型是 moment-interval，也就是某个时间或是一段时间。它代表的是出于业务或法律原因需要记录和跟踪的事情，是在某个时间或时间段内发生的事情。它帮助提醒我们在问题领域中寻找重要的时刻或时间段。 
比如，销售（Sale）是在某一时刻进行的（moment），这里重要的信息是销售的日期和时间；比如，租赁（Rental）则发生在一段时间内，这个时间段就是从支付（checkout）到归还（return）；
比如，预订（Reservation）也是发生在一段时间内，这个时间段就是预订到使用、取消或过期。 
第二个重要原型是 role，也就是角色。角色是人、地点或事物（party-place-thing）以何种方式参与到 moment-interval 中。
比如，在销售（Sale）中，就会存在买家 (buyer) 和卖家 (seller) 两种角色。 
第三个原型是 party-place-thing，是扮演不同 role 的人（个人或组织）、地点或事物。 
第四个原型是 description，它是一种类似于目录条目的值对象，用以描述 party-place-thing 的具体数据。
使用四色法建模时，步骤如下： 首先需要寻找系统中的 moment-interval，并梳理与它前后关联的其他 moment-interval。
比如，支付（payment）作为一个 moment-interval，可能存在前置的 moment-interval 对象订单（order）然后寻找参与到 moment-interval 中的 role之后再寻找可以扮演这些 role 的 party-place-thing最后寻找 description 对象

任务
===
请根据上面描述的业务场景，按照提取概念的方法，提取其中的业务概念。并给出每个概念的定义。并以表格形式给出Glossary，并标注对应的archtype
"""

# app config
st.set_page_config(page_title="领域词典-四色建模", page_icon="🤖", layout="wide")
st.title("领域词典-四色建模")

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
