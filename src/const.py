# sqlalchemy model status
MODEL_STATUS = (
    STATUS_ALIVE,
    STATUS_DELETE,
) = range(2)

# st.session_state key
KEY_DB_CONN = "db_conn"
KEY_DB_ENGINE = "db_engine"
KEY_DB_SESSION = "db_session"

KEY_BUSINESS_CTX_ID = "business_ctx_id"
KEY_USER_STORY_ID = "user_story_id"
KEY_ACCEPTANCE_CRITERIA_ID = "acceptance_criteria_id"

KEY_BUSINESS_CTX_INDEX = "business_ctx_index"
KEY_USER_STORY_INDEX = "user_story_index"
KEY_ACCEPTANCE_CRITERIA_INDEX = "acceptance_criteria_index"
