import streamlit as st
import openai
import requests
from streamlit_lottie import st_lottie
from openai.api_resources import Completion
from openai.error import AuthenticationError
from PIL import Image

def load_lottieurl(url):
    r = requests.get(url)
    # r.status_code == 200 means retrieved info from url successfully
    if r.status_code != 200:
        return None
    return r.json()

lottie_chatbot = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_5rImXbDsO1.json")
eligible_img = Image.open("images/eligible_types.png")

def authenticate(api_key):
    try:
        openai.api_key = api_key
        Completion.create(engine="davinci", prompt="Hello")
        return True
    except AuthenticationError as e:
        st.write(str(e))
        return False
    

st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")


if "API_key" not in st.session_state:
    st.session_state["API_key"] = ""
if "API_key_valid" not in st.session_state:
    st.session_state["API_key_valid"] = False

key_link = 'https://platform.openai.com/account/api-keys'
key_text = '_Create OpenAI Key_'
key_button = f'<a href="{key_link}" target="_blank">{key_text}</a>'


with st.container():
    left_col, lottie_col = st.columns((1,1))
    with left_col:
        st.title("InfoHunter")
        st.subheader("An AI chatbot exclusive to you")
        st.write("##")
        # Get API key from user and validate
        st.markdown("**Please enter your OpenAI key** 🗝")
        st.markdown(key_button, unsafe_allow_html=True)
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
    with lottie_col:
        st_lottie(lottie_chatbot, height=300)


with st.container():
    st.write("##")
    st.write("##")
    st.write("##")
    st.image(eligible_img)