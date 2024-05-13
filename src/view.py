import streamlit as st

from models import (
    AcceptanceCriteriaModel,
    BusinessCtxModel,
    UserStoryModel,
)


def user_story_tab():

    # database models
    business_ctx_list: [BusinessCtxModel] = BusinessCtxModel.list()
    business_ctx_selectbox_options = [business_ctx_model.id for business_ctx_model in business_ctx_list]
    if "business_ctx_id" in st.session_state and st.session_state.business_ctx_id in business_ctx_selectbox_options:
        business_ctx_selectbox_index = business_ctx_selectbox_options.index(st.session_state.business_ctx_id)
        business_ctx_id = st.session_state.business_ctx_id
    elif business_ctx_selectbox_options:
        business_ctx_selectbox_index = 0
        business_ctx_id = business_ctx_selectbox_options[business_ctx_selectbox_index]
        st.session_state.business_ctx_id = business_ctx_id
    else:
        business_ctx_selectbox_index = 0
        business_ctx_id = None

    user_story_list: [UserStoryModel] = UserStoryModel.list(
        UserStoryModel.business_ctx_id == business_ctx_id
    )
    user_story_selectbox_options = [user_story_model.id for user_story_model in user_story_list]
    if "user_story_id" in st.session_state and st.session_state.user_story_id in user_story_selectbox_options:
        user_story_selectbox_index = user_story_selectbox_options.index(st.session_state.user_story_id)
        user_story_id = st.session_state["user_story_id"]
    else:
        user_story_selectbox_index = 0
        if user_story_selectbox_options:
            user_story_id = user_story_selectbox_options[user_story_selectbox_index]
        else:
            user_story_id = None

    acceptance_criteria_list: [AcceptanceCriteriaModel] = AcceptanceCriteriaModel.list(
        AcceptanceCriteriaModel.user_story_id == user_story_id,
    )
    acceptance_criteria_selectbox_options = [
        acceptance_criteria_model.id for acceptance_criteria_model in acceptance_criteria_list
    ]
    if "acceptance_criteria_id" in st.session_state and \
            st.session_state.acceptance_criteria_id in acceptance_criteria_selectbox_options:
        acceptance_criteria_selectbox_index = acceptance_criteria_selectbox_options.index(
            st.session_state.acceptance_criteria_id
        )
    else:
        acceptance_criteria_selectbox_index = 0

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
        confirm = dialog_left_column.button("Confirm", type="primary")
        dialog_right_column.button("Cancel")
        if confirm:
            # models.UserStoryModel.delete_by_id(st.session_state.user_story_id)
            UserStoryModel.get(st.session_state.user_story_id).delete()
            st.rerun()

    def format_acceptance_criteria_selectbox(acceptance_criteria_id):
        acceptance_criteria_model: AcceptanceCriteriaModel = AcceptanceCriteriaModel.get(
            acceptance_criteria_id,
        )
        if acceptance_criteria_model:
            acceptance_criteria_title = acceptance_criteria_model.title
        else:
            acceptance_criteria_title = f"验收标准已被删除，ID={acceptance_criteria_model}"
        return acceptance_criteria_title

    def format_acceptance_criteria_text_area(acceptance_criteria_id):
        if acceptance_criteria_id is None:
            return ""
        acceptance_criteria_model: AcceptanceCriteriaModel = AcceptanceCriteriaModel.get(
            acceptance_criteria_id,
        )
        if acceptance_criteria_model:
            acceptance_criteria_content = acceptance_criteria_model.content
        else:
            acceptance_criteria_content = f"验收标准已被删除，ID={acceptance_criteria_model}"
        return acceptance_criteria_content

    def on_change_acceptance_criteria_content():
        acceptance_criteria_id = st.session_state.acceptance_criteria_id
        acceptance_criteria_content = st.session_state.acceptance_criteria_content
        if acceptance_criteria_id is None:
            # RuntimeError: Could not find fragment with id
            # dialog_add_acceptance_criteria(acceptance_criteria_content)
            return
        acceptance_criteria_model = AcceptanceCriteriaModel.get(
            acceptance_criteria_id,
        )
        acceptance_criteria_model.content = acceptance_criteria_content
        acceptance_criteria_model.save()

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

    # user story columns
    left_column_us, right_column_us = st.columns([0.9, 0.1])

    with left_column_us:
        acceptance_criteria_selectbox_id = st.selectbox(
          "User Story List",
          options=user_story_selectbox_options,
          key="user_story_id",
          format_func=format_user_story_selectbox,
          index=user_story_selectbox_index,
        )

    with right_column_us:
        container = st.container(height=12, border=False)
        with st.popover(
                label="操作",
                use_container_width=True,  # 宽度适配父容器
        ):
            button_add_clicked = st.button(
                "添加",
                disabled=not st.session_state.get("business_ctx_id"),
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
            format_user_story_text_area(st.session_state.user_story_id),
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

    # acceptance criteria columns
    left_column_ac, right_column_ac = st.columns([0.9, 0.1])

    with left_column_ac:
        acceptance_criteria_selectbox_id = st.selectbox(
          "Acceptance Criteria List",
          options=acceptance_criteria_selectbox_options,
          key="acceptance_criteria_id",
          format_func=format_acceptance_criteria_selectbox,
          index=acceptance_criteria_selectbox_index,
        )

    with right_column_ac:
        container = st.container(height=12, border=False)
        with st.popover(
                label="操作",
                use_container_width=True,  # 宽度适配父容器
        ):
            button_add_clicked = st.button(
                "添加",
                key="button_add_ac",
                disabled=not st.session_state.get("user_story_id"),
            )
            button_modify_clicked = st.button(
                "修改",
                key="button_modify_ac",
                disabled=not acceptance_criteria_selectbox_options,
            )
            button_delete_clicked = st.button(
                "删除",
                key="button_delete_ac",
                disabled=not acceptance_criteria_selectbox_options,
                type="primary",
            )

        if button_add_clicked:
            dialog_add_acceptance_criteria()
        if button_modify_clicked:
            dialog_modify_acceptance_criteria_title()
        if button_delete_clicked:
            dialog_delete_acceptance_criteria()

    if st.session_state.acceptance_criteria_id:
        acceptance_criteria = st.text_area(
            "Acceptance Criteria",
            format_acceptance_criteria_text_area(acceptance_criteria_selectbox_id),
            key="acceptance_criteria_content",
            height=300,
            on_change=on_change_acceptance_criteria_content,
        )
    else:
        acceptance_criteria = st.text_area(
            "User Story",
            # disabled=True,
            key="acceptance_criteria_content",
            height=300,
            # on_change=on_change_acceptance_criteria_content,
        )
        if acceptance_criteria:
            dialog_add_acceptance_criteria(acceptance_criteria)

    # TODO st.selectbox business_ctx

    business_ctx = st.text_area(
        "Business Context",
        format_business_ctx_text_area(business_ctx_id),
        key="business_ctx_content",
        height=300,
        on_change=on_change_user_business_ctx,
    )
    return user_story, business_ctx
