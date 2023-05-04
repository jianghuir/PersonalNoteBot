import streamlit as st
import openai
from openai.api_resources import Completion
from openai.error import AuthenticationError

st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")

with st.container():
    st.title("InfoHunter")
    st.subheader("这里放app功能简介: <InfoHunter helps to index your files and answer questions ...>")


    st.write("##")
    st.subheader("Please enter your OpenAI API key 🗝")
    


if "API_key" not in st.session_state:
    st.session_state["API_key"] = ""
if "API_key_valid" not in st.session_state:
    st.session_state["API_key_valid"] = False


def authenticate(api_key):
    try:
        openai.api_key = api_key
        Completion.create(engine="davinci", prompt="Hello")
        return True
    except AuthenticationError as e:
        st.write(str(e))
        return False

# Get API key from user and validate
with st.container():
    st.write("You can create your API key at https://platform.openai.com/account/api-keys")
    API_key = st.text_input("Your OpenAI key:", st.session_state["API_key"], type="password")
    st.session_state["API_key"] = API_key
    validate_key = st.button("Validate API Key")
    if validate_key:
        if authenticate(API_key):
            st.success("Authentication successful")
            st.session_state["API_key_valid"] = True    
        else:
            st.error("The key is invalid")
            st.session_state["API_key_valid"] = False


with st.container():
    st.write("##")
    st.subheader("Eligible File Type:")
    st.write("insert file types and images here")