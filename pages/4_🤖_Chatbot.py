import streamlit as st
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain import OpenAI
from langchain.chains import RetrievalQA, ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain.agents import Tool, initialize_agent
from streamlit_chat import message
from utilities import load_database_self, db_folder
from PIL import Image

st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

img_bot = Image.open("images/bot2.png")
st.sidebar.success("Select a page above")
no_idx = "Do not use any database"

if "API_key" not in st.session_state:
    st.session_state["API_key"] = ""
if "API_key_valid" not in st.session_state:
    st.session_state["API_key_valid"] = False
if "query_history" not in st.session_state:
    st.session_state["query_history"] = []
if "response_history" not in st.session_state:
    st.session_state["response_history"] = []
if "chatbot" not in st.session_state:
    st.session_state["chatbot"] = None
if "index" not in st.session_state:
    st.session_state["index"] = no_idx
if "query_text" not in st.session_state:
    st.session_state["query_text"] = ""
if "text_value" not in st.session_state:
    st.session_state["text_value"] = ""

record_self = load_database_self()

def update():
    st.session_state.query_text = st.session_state.text_value
    return

def init_chatbot(selected_index):
    """
    This function initiates a Chatbot
    If an index is selected, the index is wrapped as a tool;
    if no index is used, the bot is a simple OpenAI
    """    
    llm = OpenAI(
        temperature=0.2,
        openai_api_key=st.session_state["API_key"],
        model_name="text-davinci-003",
    )

    if selected_index != no_idx:
        index_path = os.path.join(os.getcwd(), db_folder, selected_index)
        n_vectors = record_self.loc[record_self.Index==selected_index, "vector counts"].squeeze()
        if n_vectors > 4:
            k = 4
        else:
            k = int(n_vectors)
        
        embeddings = OpenAIEmbeddings(openai_api_key=st.session_state["API_key"])
        vectordb = Chroma(persist_directory=index_path, embedding_function=embeddings)

        # chatbot QA function
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff', 
            retriever=vectordb.as_retriever(search_kwargs={"k":k})
        )

        source_tool = Tool(
            name="retrievalQA tool",
            func=qa.run,
            description="Useful when answering questions",
        )

        memory = ConversationSummaryMemory(llm=llm,memory_key="chat_history")

        tools = [source_tool]

        conversational_agent = initialize_agent(
            agent='conversational-react-description', 
            tools=tools, 
            llm=llm,
            verbose=True,
            max_iterations=3,
            memory=memory,
        )
        chatbot = conversational_agent

    else:
        memory2 = ConversationSummaryMemory(llm=llm)
        summary_no_tool = ConversationChain(llm=llm,memory=memory2)
        chatbot = summary_no_tool

    return chatbot


with st.container():
    image_column, right_column = st.columns((1,2))
    with image_column:
        st.image(img_bot)
    with right_column:
        st.subheader("Your Personal Chatbot ")
        st.write("Your personal AI chatbot will initially attempt to answer your question using the \
knowledge contained within your document database. If the question exceeds the scope of the documents, the \
chatbot will then endeavor to answer based on its own knowledge.")


options = list(record_self.Index.values)
options += [no_idx]
current_option = options.index(st.session_state["index"])
st.markdown("Select a database")
selected_index = st.selectbox("Select an index for Chatbot", options, label_visibility="collapsed")

initiate_chatbot = st.button("Initiate Chatbot 🤖")

# make the language model for chatbot
if not st.session_state["API_key_valid"]:
    st.error("Please validate your OpenAI key at Homepage.")
else:
    if initiate_chatbot:        
        st.session_state["chatbot"] = init_chatbot(selected_index) #update chatbot
        st.session_state["index"] = selected_index #update chatbot
        initiate_chatbot = False #Important! must disable repeated activation of chatbot 
    
    if st.session_state["chatbot"]:
        if st.session_state["index"] == no_idx:
            st.success("The Chatbot 🤖 is ready to answer your questions! (no database loaded)")
        else:
            st.success(f"The Chatbot 🤖 loaded with **- {st.session_state['index']} -** is ready to answer your questions!")       

        # we need to use st.form to clear query after submission
        with st.form(key='my_form',clear_on_submit=True):
            st.text_input('Enter your question', value="", key='text_value')
            submit = st.form_submit_button(label='Submit', on_click=update)

        query = st.session_state.query_text            
        st.session_state.query_text = "" #clear query_text, so in next round query will start from none

        if query:
            with st.spinner("🤖 generating answer..."):
                instruction = "AI must use retrievalQA tool first. If cannot find answer in retrievalQA tool, \
AI's output must start with 'The question is not in the scope of the documents provided.', and then \
AI can answer the question based on chat history or parametric knowledge. Question: "

                if st.session_state["index"] == no_idx:
                    response = st.session_state["chatbot"](query)
                    #st.write(response)
                else:
                    full_query = instruction + query
                    response = st.session_state["chatbot"](full_query)
                    #st.write(response)
                # Store the user input and response
                st.session_state.query_history.append(query)
                if st.session_state["index"] == no_idx:
                    st.session_state.response_history.append(response["response"])
                else:
                    st.session_state.response_history.append(response["output"])
                st.spinner("")
            

# Display the updated chat history
for i in range(len(st.session_state.query_history)-1, -1, -1):
    message(st.session_state.response_history[i], is_user=False, key=str(i)+"_AI",seed=727)
    message(st.session_state.query_history[i], is_user=True, key=str(i)+"_user")
            
            
        





