import streamlit as st
from streamlit.logger import get_logger
from typing import List

from models import (
    # AcceptanceCriteriaModel,
    # BusinessCtxModel,
    UserStoryModel,
)
import const

log = get_logger(__name__)


def user_story():
    # database models
    user_story_selectbox_options = [user_story_model.id for user_story_model in UserStoryModel.list()]

    # business_ctx_list: [BusinessCtxModel] = BusinessCtxModel.list()
    # business_ctx_selectbox_options = [business_ctx_model.id for business_ctx_model in business_ctx_list]
    # if "business_ctx_id" in st.session_state and st.session_state.business_ctx_id in business_ctx_selectbox_options:
    #     # business_ctx_selectbox_index = business_ctx_selectbox_options.index(st.session_state.business_ctx_id)
    #     business_ctx_id = st.session_state.business_ctx_id
    # elif business_ctx_selectbox_options:
    #     # business_ctx_selectbox_index = 0
    #     business_ctx_id = business_ctx_selectbox_options[0]
    #     st.session_state.business_ctx_id = business_ctx_id
    # else:
    #     # business_ctx_selectbox_index = 0
    #     business_ctx_id = None
    #     st.session_state.business_ctx_id = None
    # log.debug(f"{business_ctx_id=} {st.session_state.business_ctx_id=}")
    #
    # user_story_list: [UserStoryModel] = UserStoryModel.list(
    #     UserStoryModel.business_ctx_id == business_ctx_id
    # )
    # user_story_selectbox_options = [user_story_model.id for user_story_model in user_story_list]
    # if "user_story_id" in st.session_state and st.session_state.user_story_id in user_story_selectbox_options:
    #     user_story_selectbox_index = user_story_selectbox_options.index(st.session_state.user_story_id)
    #     user_story_id = st.session_state["user_story_id"]
    # elif user_story_selectbox_options:
    #     user_story_selectbox_index = 0
    #     user_story_id = user_story_selectbox_options[user_story_selectbox_index]
    #     st.session_state.user_story_id = user_story_id
    # else:
    #     user_story_selectbox_index = 0
    #     user_story_id = None
    #     st.session_state.user_story_id = None
    # log.debug(f"{user_story_selectbox_index=} {user_story_id=} {st.session_state.user_story_id=}")
    #
    # acceptance_criteria_list: [AcceptanceCriteriaModel] = AcceptanceCriteriaModel.list(
    #     AcceptanceCriteriaModel.user_story_id == user_story_id,
    # )
    # acceptance_criteria_selectbox_options = [
    #     acceptance_criteria_model.id for acceptance_criteria_model in acceptance_criteria_list
    # ]
    # if "acceptance_criteria_id" in st.session_state and \
    #         st.session_state.acceptance_criteria_id in acceptance_criteria_selectbox_options:
    #     # acceptance_criteria_selectbox_index = acceptance_criteria_selectbox_options.index(
    #     #     st.session_state.acceptance_criteria_id
    #     # )
    #     acceptance_criteria_id = st.session_state.acceptance_criteria_id
    # elif acceptance_criteria_selectbox_options:
    #     # acceptance_criteria_selectbox_index = 0
    #     acceptance_criteria_id = acceptance_criteria_selectbox_options[0]
    #     st.session_state.acceptance_criteria_id = acceptance_criteria_id
    # else:
    #     # acceptance_criteria_selectbox_index = None
    #     acceptance_criteria_id = None
    #     st.session_state.acceptance_criteria_id = None
    # log.debug(f"{acceptance_criteria_id=} {st.session_state.acceptance_criteria_id=}")

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

    def format_business_ctx_selectbox(format_business_ctx_id):
        business_ctx_model = BusinessCtxModel.get(
            format_business_ctx_id,
        )
        if business_ctx_model:
            business_ctx_title = business_ctx_model.title
        else:
            business_ctx_title = f"业务背景已被删除，ID={business_ctx_model}"
        return business_ctx_title

    def format_business_ctx_text_area(format_business_ctx_id):
        if format_business_ctx_id is None:
            return ""
        business_ctx_model = BusinessCtxModel.get(
            format_business_ctx_id,
        )
        if business_ctx_model:
            business_ctx_content = business_ctx_model.content
        else:
            business_ctx_content = f"业务背景已被删除，ID={business_ctx_model}"
        return business_ctx_content

    def on_change_user_story_list():
        print("on_change_user_story_list")
        if "user_story_content" in st.session_state:
            del st.session_state["user_story_content"]

    def on_change_user_story_content():
        on_change_user_story_id = st.session_state.user_story_id
        user_story_content = st.session_state.user_story_content
        if on_change_user_story_id is None:
            # dialog_add_user_story(user_story_content)  # RuntimeError: Could not find fragment with id
            return
        user_story_model = UserStoryModel.get(st.session_state.user_story_id)
        user_story_model.content = user_story_content
        user_story_model.save()

    def on_change_user_business_ctx():
        on_change_business_ctx_id = st.session_state.business_ctx_id
        business_ctx_content = st.session_state.business_ctx_content
        if on_change_business_ctx_id:
            business_ctx_model = BusinessCtxModel.get(
                on_change_business_ctx_id,
            )
            if business_ctx_model:
                business_ctx_model.content = business_ctx_content
        else:
            business_ctx_model = BusinessCtxModel(
                content=business_ctx_content,
            ).save()
            st.session_state.business_ctx_id = business_ctx_model.id
        business_ctx_model.save()

    @st.experimental_dialog("new user story")
    def dialog_add_user_story(content=""):
        user_story_title = st.text_input("title")
        if st.button("Submit"):
            user_story_model = UserStoryModel(
                business_ctx_id=st.session_state.business_ctx_id,
                title=user_story_title,
                content=content,
            ).save()
            st.session_state.user_story_id = user_story_model.id
            st.session_state.user_story_text_status = const.TEXT_STATUS_SAVE
            st.rerun()

    @st.experimental_dialog("modify user story title")
    def dialog_modify_user_story_title():
        user_story_title = st.text_input("title", format_user_story_selectbox(st.session_state.user_story_id))
        if st.button("Submit"):
            user_story_model = UserStoryModel.get(st.session_state.user_story_id)
            user_story_model.title = user_story_title
            user_story_model.save()
            st.rerun()

    @st.experimental_dialog("delete user story")
    def dialog_delete_user_story():
        dialog_left_column, dialog_right_column = st.columns(2)
        if dialog_left_column.button("Confirm", type="primary"):
            # models.UserStoryModel.delete_by_id(st.session_state.user_story_id)
            UserStoryModel.get(st.session_state.user_story_id).delete()
            st.rerun()
        if dialog_right_column.button("Cancel"):
            st.rerun()

    def format_acceptance_criteria_selectbox(format_acceptance_criteria_id):
        acceptance_criteria_model: AcceptanceCriteriaModel = AcceptanceCriteriaModel.get(
            format_acceptance_criteria_id,
        )
        if acceptance_criteria_model:
            acceptance_criteria_title = acceptance_criteria_model.title
        else:
            acceptance_criteria_title = f"验收标准已被删除，ID={acceptance_criteria_model}"
        return acceptance_criteria_title

    def format_acceptance_criteria_text_area(format_acceptance_criteria_id):
        if format_acceptance_criteria_id is None:
            return ""
        acceptance_criteria_model: AcceptanceCriteriaModel = AcceptanceCriteriaModel.get(
            format_acceptance_criteria_id,
        )
        if acceptance_criteria_model:
            acceptance_criteria_content = acceptance_criteria_model.content
        else:
            acceptance_criteria_content = f"验收标准已被删除，ID={acceptance_criteria_model}"
        return acceptance_criteria_content

    def on_change_acceptance_criteria_content():
        on_change_acceptance_criteria_id = st.session_state.acceptance_criteria_id
        acceptance_criteria_content = st.session_state.acceptance_criteria_content
        if on_change_acceptance_criteria_id:
            acceptance_criteria_model = AcceptanceCriteriaModel.get(
                on_change_acceptance_criteria_id,
            )
            acceptance_criteria_model.content = acceptance_criteria_content
            acceptance_criteria_model.save()
        else:
            # RuntimeError: Could not find fragment with id
            # dialog_add_acceptance_criteria(acceptance_criteria_content)

            acceptance_criteria_model = AcceptanceCriteriaModel(
                user_story_id=st.session_state.user_story_id,
                content=acceptance_criteria_content,
            ).save()
            st.session_state.acceptance_criteria_id = acceptance_criteria_model.id

    @st.experimental_dialog("new acceptance criteria")
    def dialog_add_acceptance_criteria(content=""):
        acceptance_criteria_title = st.text_input("title")
        if st.button("Submit"):
            acceptance_criteria_model = AcceptanceCriteriaModel(
                user_story_id=st.session_state.user_story_id,
                title=acceptance_criteria_title,
                content=content,
            ).save()
            st.session_state.acceptance_criteria_id = acceptance_criteria_model.id
            st.rerun()

    @st.experimental_dialog("modify user acceptance criteria")
    def dialog_modify_acceptance_criteria_title():
        acceptance_criteria_title = st.text_input(
            "title",
            format_acceptance_criteria_selectbox(st.session_state.acceptance_criteria_id)
        )
        if st.button("Submit"):
            acceptance_criteria_model = AcceptanceCriteriaModel.get(
                st.session_state.acceptance_criteria_id,
            )
            acceptance_criteria_model.title = acceptance_criteria_title
            acceptance_criteria_model.save()
            st.rerun()

    @st.experimental_dialog("delete acceptance criteria")
    def dialog_delete_acceptance_criteria():
        dialog_left_column, dialog_right_column = st.columns(2)
        confirm = dialog_left_column.button("Confirm", type="primary")
        dialog_right_column.button("Cancel")
        if confirm:
            AcceptanceCriteriaModel.get(st.session_state.acceptance_criteria_id).delete()
            st.rerun()

    # with left_column_us:
    #     user_story_id = st.selectbox(
    #         "User Story List",
    #         options=user_story_selectbox_options,
    #         key="user_story_id",
    #         format_func=format_user_story_selectbox,
    #         index=user_story_selectbox_index,
    #         # on_change=on_change_user_story_list(),
    #     )
    user_story_id = st.selectbox(
        "User Story List",
        options=user_story_selectbox_options,
        key="user_story_id",
        format_func=format_user_story_selectbox,
        index=user_story_selectbox_index,
        # on_change=on_change_user_story_list(),
    )

    # with right_column_us:
    #     st.container(height=12, border=False)
    #     with st.popover(
    #             label="操作",
    #             use_container_width=True,  # 宽度适配父容器
    #     ):
    # with right_column_us_add:
    #     st.container(height=12, border=False)
    #     button_add_clicked = st.button(
    #         "添加",
    #         disabled=not st.session_state.get("business_ctx_id"),
    #     )
    # with right_column_us_modify:
    #     st.container(height=12, border=False)
    #     button_modify_clicked = st.button(
    #         "修改",
    #         disabled=not user_story_selectbox_options,
    #     )
    # with right_column_us_delete:
    #     st.container(height=12, border=False)
    #     button_delete_clicked = st.button(
    #         "删除",
    #         disabled=not user_story_selectbox_options,
    #         type="primary",
    #     )
    #
    # if button_add_clicked:
    #     dialog_add_user_story()
    # if button_modify_clicked:
    #     dialog_modify_user_story_title()
    # if button_delete_clicked:
    #     dialog_delete_user_story()

    # if st.session_state.user_story_id:
    #     user_story = st.text_area(
    #         "User Story",
    #         format_user_story_text_area(user_story_id),
    #         key="user_story_content",
    #         height=300,
    #         on_change=on_change_user_story_content,
    #     )
    # else:
    #     user_story = st.text_area(
    #         "User Story",
    #         # disabled=True,
    #         key="user_story_content",
    #         height=300,
    #         # on_change=on_change_user_story_content,
    #     )
    #     if user_story:
    #         dialog_add_user_story(user_story)

    # if st.session_state.get("user_story_content"):
    #     text_area_value = st.session_state["user_story_content"]
    # elif user_story_id:
    #     text_area_value = format_user_story_text_area(user_story_id)
    # else:
    #     text_area_value = ""
    if user_story_id:
        text_area_value = format_user_story_text_area(user_story_id)
    else:
        text_area_value = ""

    user_story = st.text_area(
        "User Story",
        text_area_value,
        # disabled=True,
        key="user_story_content",
        height=300,
        disabled=not business_ctx_id,
        placeholder="please input" if business_ctx_id else "need business ctx",
        label_visibility="collapsed",
    )

    st.session_state.setdefault("user_story_text_status", const.TEXT_STATUS_INIT)
    if (user_story_id and format_user_story_text_area(user_story_id) != user_story) \
            or (not user_story_id and user_story):
        st.session_state["user_story_text_status"] = const.TEXT_STATUS_CHANGE
    elif st.session_state.get("user_story_text_status") == const.TEXT_STATUS_CHANGE:
        st.session_state["user_story_text_status"] = const.TEXT_STATUS_INIT

    # user story columns
    if st.session_state.get("user_story_text_status") == const.TEXT_STATUS_SAVE:
        (
            right_column_us_save,
            right_column_us_add,
            # right_column_us_modify,
            right_column_us_delete,
            left_column_us_info,
        ) = st.columns([1, 1, 1, 3])
        left_column_ac_info = left_column_us_info
    else:
        (
            right_column_us_save,
            right_column_us_add,
            # right_column_us_modify,
            right_column_us_delete,
            left_column_us_info,
            left_column_ac_info,
        ) = st.columns([1, 1, 1, 3, 3])
    with right_column_us_add:
        button_add_clicked = st.button(
            "新增",
            disabled=not st.session_state.get("business_ctx_id"),
        )
    # with right_column_us_modify:
    #     st.container(height=12, border=False)
    #     button_modify_clicked = st.button(
    #         "修改",
    #         disabled=not user_story_selectbox_options,
    #     )
    with right_column_us_delete:
        button_delete_clicked = st.button(
            "删除",
            disabled=not user_story_selectbox_options,
            type="primary",
        )

    if button_add_clicked:
        dialog_add_user_story()
    # if button_modify_clicked:
    #     dialog_modify_user_story_title()
    if button_delete_clicked:
        dialog_delete_user_story()

    with right_column_us_save:
        button_save_user_story_clicked = st.button(
            "保存",
        )
    if button_save_user_story_clicked:
        if st.session_state.user_story_id:
            user_story_model = UserStoryModel.get(st.session_state.user_story_id)
            user_story_model.content = user_story
            user_story_model.save()
            st.session_state.user_story_text_status = const.TEXT_STATUS_SAVE

            # save acceptance criteria
            on_change_acceptance_criteria_content()
            st.session_state.ac_text_status = const.TEXT_STATUS_SAVE
        else:
            dialog_add_user_story(user_story)

    with left_column_us_info:
        user_story_text_status = st.session_state.get("user_story_text_status")
        if user_story_text_status == const.TEXT_STATUS_INIT:
            pass
        elif user_story_text_status == const.TEXT_STATUS_CHANGE:
            st.warning('user story unsaved', icon="ℹ")
        elif user_story_text_status == const.TEXT_STATUS_SAVE:
            del st.session_state["user_story_text_status"]
            # st.info('save success', icon="ℹ")
            st.toast('save success', icon='🎉')
        else:
            st.error(f'unknown user_story_text_status={user_story_text_status}')

    # acceptance criteria columns
    # left_column_ac, right_column_ac = st.columns([0.9, 0.1])
    #
    # with left_column_ac:
    #     acceptance_criteria_selectbox_id = st.selectbox(
    #       "Acceptance Criteria List",
    #       options=acceptance_criteria_selectbox_options,
    #       key="acceptance_criteria_id",
    #       format_func=format_acceptance_criteria_selectbox,
    #       index=acceptance_criteria_selectbox_index,
    #     )
    #
    # with right_column_ac:
    #     container = st.container(height=12, border=False)
    #     with st.popover(
    #             label="操作",
    #             use_container_width=True,  # 宽度适配父容器
    #     ):
    #         button_add_clicked = st.button(
    #             "添加",
    #             key="button_add_ac",
    #             disabled=not st.session_state.get("user_story_id"),
    #         )
    #         button_modify_clicked = st.button(
    #             "修改",
    #             key="button_modify_ac",
    #             disabled=not acceptance_criteria_selectbox_options,
    #         )
    #         button_delete_clicked = st.button(
    #             "删除",
    #             key="button_delete_ac",
    #             disabled=not acceptance_criteria_selectbox_options,
    #             type="primary",
    #         )
    #
    #     if button_add_clicked:
    #         dialog_add_acceptance_criteria()
    #     if button_modify_clicked:
    #         dialog_modify_acceptance_criteria_title()
    #     if button_delete_clicked:
    #         dialog_delete_acceptance_criteria()
    #
    # if acceptance_criteria_id:
    #     acceptance_criteria = st.text_area(
    #         "Acceptance Criteria",
    #         format_acceptance_criteria_text_area(acceptance_criteria_id),
    #         key="acceptance_criteria_content",
    #         height=300,
    #         on_change=on_change_acceptance_criteria_content,
    #     )
    # else:
    #     acceptance_criteria = st.text_area(
    #         "Acceptance Criteria",
    #         # disabled=True,
    #         key="acceptance_criteria_content",
    #         height=300,
    #         placeholder="please input",
    #         # on_change=on_change_acceptance_criteria_content,
    #     )
    #     if acceptance_criteria:
    #         dialog_add_acceptance_criteria(acceptance_criteria)

    # acceptance_criteria = st.text_area(
    #     "Acceptance Criteria",
    #     format_acceptance_criteria_text_area(acceptance_criteria_id),
    #     key="acceptance_criteria_content",
    #     height=300,
    #     placeholder="please input",
    #     on_change=on_change_acceptance_criteria_content,
    # )

    if acceptance_criteria_id:
        text_area_value = format_acceptance_criteria_text_area(acceptance_criteria_id)
    else:
        text_area_value = ""

    acceptance_criteria = st.text_area(
        "Acceptance Criteria",
        text_area_value,
        key="acceptance_criteria_content",
        height=300,
        disabled=not user_story_id,
        placeholder="please input" if user_story_id else "need user story",
    )
    st.session_state.setdefault("ac_text_status", const.TEXT_STATUS_INIT)
    if (acceptance_criteria_id and
        format_acceptance_criteria_text_area(acceptance_criteria_id) != acceptance_criteria) \
            or (not acceptance_criteria_id and acceptance_criteria):
        st.session_state["ac_text_status"] = const.TEXT_STATUS_CHANGE
    elif st.session_state.get("ac_text_status") == const.TEXT_STATUS_CHANGE:
        st.session_state["ac_text_status"] = const.TEXT_STATUS_INIT

    with left_column_ac_info:
        ac_text_status = st.session_state.get("ac_text_status")
        if ac_text_status == const.TEXT_STATUS_INIT:
            pass
        elif ac_text_status == const.TEXT_STATUS_CHANGE:
            st.warning('ac unsaved', icon="ℹ")
        elif ac_text_status == const.TEXT_STATUS_SAVE:
            del st.session_state["ac_text_status"]
            # st.info('save success', icon="ℹ")
        else:
            st.error(f'unknown ac_text_status={ac_text_status}')

    # right_column_bc_save, left_column_bc_save = st.columns([0.4, 0.6])
    # with right_column_bc_save:
    #     button_save_acceptance_criteria_clicked = st.button(
    #         "保存",
    #         key="button_save_acceptance_criteria_clicked"
    #     )
    # if button_save_acceptance_criteria_clicked:
    #     on_change_acceptance_criteria_content()
    #     st.session_state.ac_text_status = const.TEXT_STATUS_SAVE
    # with left_column_bc_save:
    #     ac_text_status = st.session_state.get("ac_text_status")
    #     if ac_text_status == const.TEXT_STATUS_INIT:
    #         pass
    #     elif ac_text_status == const.TEXT_STATUS_CHANGE:
    #         st.warning('unsaved', icon="ℹ")
    #     elif ac_text_status == const.TEXT_STATUS_SAVE:
    #         del st.session_state["ac_text_status"]
    #         st.info('save success', icon="ℹ")
    #     else:
    #         st.error(f'unknown ac_text_status={ac_text_status}')

    # TODO st.selectbox business_ctx

    # business_ctx = st.text_area(
    #     "Business Context",
    #     format_business_ctx_text_area(business_ctx_id),
    #     key="business_ctx_content",
    #     height=300,
    #     on_change=on_change_user_business_ctx,
    # )

    st.session_state.setdefault("business_ctx_text_status", const.TEXT_STATUS_INIT)
    if business_ctx_id:
        text_area_value = format_business_ctx_text_area(business_ctx_id)
    else:
        text_area_value = ""

    business_ctx = st.text_area(
        "Business Context",
        text_area_value,
        key="business_ctx_content",
        height=300,
        # on_change=on_change_user_business_ctx,
    )
    if (business_ctx_id and format_business_ctx_text_area(business_ctx_id) != business_ctx) \
            or (not business_ctx_id and business_ctx):
        st.session_state["business_ctx_text_status"] = const.TEXT_STATUS_CHANGE
    elif st.session_state.get("business_ctx_text_status") == const.TEXT_STATUS_CHANGE:
        st.session_state["business_ctx_text_status"] = const.TEXT_STATUS_INIT

    right_column_bc_save, left_column_bc_save = st.columns([0.2, 0.6])
    with right_column_bc_save:
        button_save_business_ctx_clicked = st.button(
            "保存",
            key="button_save_business_ctx_clicked"
        )
    if button_save_business_ctx_clicked:
        on_change_user_business_ctx()
        st.session_state.business_ctx_text_status = const.TEXT_STATUS_SAVE
    with left_column_bc_save:
        business_ctx_text_status = st.session_state.get("business_ctx_text_status")
        if business_ctx_text_status == const.TEXT_STATUS_INIT:
            pass
        elif business_ctx_text_status == const.TEXT_STATUS_CHANGE:
            st.warning('unsaved', icon="ℹ")
        elif business_ctx_text_status == const.TEXT_STATUS_SAVE:
            del st.session_state["business_ctx_text_status"]
            st.info('save success', icon="ℹ")
        else:
            st.error(f'unknown business_ctx_text_status={business_ctx_text_status}')
    return user_story, business_ctx
