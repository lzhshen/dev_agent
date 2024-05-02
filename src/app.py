import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from streamlit_float import *


# app config
st.set_page_config(page_title="Streaming bot", page_icon="🤖", layout="wide")
st.title("Streaming bot")

float_init(theme=True, include_unstable_primary=False)

load_dotenv()

def get_response(user_query, chat_history):

    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI()
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })

left_column, right_column = st.columns(2)

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

with left_column:    
    with st.container(border=border, height=800):
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
            user_query = st.chat_input("What is up?")
            button_b_pos = "0rem"
            button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            float_parent(css=button_css)

        if user_query is not None and user_query != "":
            st.session_state.chat_history.append(HumanMessage(content=user_query))

            with st.chat_message("Human"):
                st.markdown(user_query)

            with st.chat_message("AI"):
                response = st.write_stream(get_response(user_query, st.session_state.chat_history))

            st.session_state.chat_history.append(AIMessage(content=response))

with right_column:
    user_story = st.text_area(
        "User Story",
        "...",
        height= 300,
    )

    business_ctx = st.text_area(
        "Business Context",
        "It was the best of times, it was the worst of times, it was the age of "
        "wisdom, it was the age of foolishness, it was the epoch of belief, it "
        "was the epoch of incredulity, it was the season of Light, it was the "
        "season of Darkness, it was the spring of hope, it was the winter of "
        "despair, (...)",
        height= 300,
    )
