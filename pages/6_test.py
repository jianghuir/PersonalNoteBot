# https://www.youtube.com/watch?v=nwsXGrxX_Hw&t=33s  chatbot streamlit
# from transformers import BlenderbotTokenizer
# from transformers import BlenderbotForConditionalGeneration

import streamlit as st
from streamlit_chat import message
from PIL import Image


#st.help(message)
# Example chat history
chat_history = [
    {"speaker": "user", "text": "Hello!"},
    {"speaker": "bot", "text": "Hi there, how can I help you today?"},
    {"speaker": "user", "text": "I have a question about your product."},
    {"speaker": "bot", "text": "Sure, what would you like to know?"}
]

# Display the chat history
for msg in chat_history:
    if msg["speaker"] == "user":
        message(msg["text"], is_user=True)
    else:
        message(msg["text"], seed=727)

message("My message") 
message("Hello bot!", is_user=True)  # align's the message to the right

st.write("Test streamlit button. 同一时间只能有一个button为True，切换页面会使所有button变成False")
button1 = st.button("button1")
st.write("button1:", button1)
button2 = st.button("button2")
st.write("button1:", button1, ".  button2:", button2)

st.write("Test how to clear a text input box")
if "q" not in st.session_state:
    st.session_state["q"] = ""

query = st.text_input("enter query", value=st.session_state["q"])
st.write(query)




# this method is useless, because clear button doesn't return text2
def clear_form():
    st.session_state["foo"] = ""
    st.session_state["bar"] = ""
    
with st.form("myform"):
    f1, f2 = st.columns([1, 1])
    with f1:
        text1 = st.text_input("Foo", key="foo")
    with f2:
        text2 = st.text_input("Bar", key="bar")
    f3, f4 = st.columns([1, 1])
    with f3:
        submit = st.form_submit_button(label="Submit")
    with f4:
        clear = st.form_submit_button(label="Clear", on_click=clear_form)

if submit:
    st.write('Submitted')
    st.write(text1)
    st.write(submit)

if clear:
    st.write('Cleared')
    st.write(clear)
    st.write(text2)
    st.write(text1)
    st.write(type(clear))

if text2:
    st.write(text2)




st.title('Input Example')
if 'text' not in st.session_state:
    st.session_state.text = ""

def update():
    st.session_state.text = st.session_state.text_value

with st.form(key='my_form',clear_on_submit=True):
    st.text_input('Enter any text', value="", key='text_value')
    submit = st.form_submit_button(label='Update', on_click=update)

st.write('text = ', st.session_state.text)

st.subheader("Test text_input(on_change=)")
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""
def generate_answer():
    m = st.session_state.input_text
    st.write(m, m) # st.write() inside on_change function doesn't really write
    return
st.text_input("enter something", key="input_text", on_change=generate_answer)
st.write(st.session_state.input_text) # must pass values through session_state for other operation