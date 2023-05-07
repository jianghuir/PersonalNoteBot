import streamlit as st
import requests
from PIL import Image


st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")


# Page Title
st.title("InfoHunter: Personal Assistant for Document Search")

# What is infoHunter section
expander = st.expander("🤔 What is InfoHunter?")

with expander:
    # Page header
    st.write("<p style='font-size: 20px; font-weight: bold;'>Description</p>", unsafe_allow_html=True)

    # Description of InfoHunter
    st.write("InfoHunter, powered by ChatGPT 3.5 and utilizing Langchain, serves as a personal assistant for document search support. This tool enables swift access to your individual notes and provides the capability to interact with them through conversation.")

    # Features section
    st.write("<p style='font-size: 20px; font-weight: bold;'>Features</p>", unsafe_allow_html=True)
    st.write("InfoHunter offers two primary features:")
    st.write("- Precise searching within your documents (Accurate Search)")
    st.write("- Interactive communication with your files (Chatbot)")
    st.write("")

    # Instructions section
    st.write("<p style='font-size: 20px; font-weight: bold;'>Instructions</p>", unsafe_allow_html=True)
    st.write("To use InfoHunter, follow these simple steps: 👍🏼")
    st.write("1. Create an OpenAI API key")
    st.write("2. Enter your folder path")
    st.write("3. Assign a name to your database")
    st.write("4. Select Accurate Search/Chatbot")
    st.write("5. Enter your queries")

# Homepage section
expander = st.expander("📚 Homepage")

with expander:

    # st.subheader("📚 Homepage")

    # Register OpenAI account and generate API key
    st.write("Prior to using InfoHunter, you will need to register an OpenAI account and generate an API key here: https://platform.openai.com/account/api-keys")
    st.write("An OpenAI API key is a unique identifier provided by OpenAI when you sign up for their API service. This key allows you to access and use OpenAI's artificial intelligence models, like ChatGPT, through their API (Application Programming Interface). It is essential to keep your API key secure, as it grants access to your account and usage of the services, which may be subject to usage limits or costs.")

# Create Database section
expander = st.expander("📝 Create Database")
with expander:

    # st.header("📝 Create Database")
    st.write("Specify a folder path where you’d like to utilize InfoHunter for document \
            interaction (e.g., you study notes, work notes, HOA documents). ")

    st.info("Absolute path is required. Examples: \n\n " 
            "Mac user: /Users/username/Documents/notes1.txt \n\n" 
            "Windows user: C:\\Users\\username\\Documents\\file.txt")

    st.write("Assign a name to your document database (e.g., note1)")
    st.write("Once you click 'submit,' InfoHunter will transform your documents into embeddings and store them in a database for further use.")

    # Supported document formats section
    st.warning("The supported document formats for InfoHunter are: \n\n" \
            "Microsoft Word (.docx), Microsoft Excel (.xlsx), Microsoft PowerPoint(.pptx) \n\n" 
            "Open Document Text(.odt), Open Document Spreadsheet(.ods) \n\n"
            "Portable Document Format(.pdf), Plain text(.txt), HyperText Markup Language(.html) \n\n"
            "Jupyter Notebook(.ipynb), Python script(.py)")

# Database section
expander = st.expander("🗂️ Database")

with expander:
    # st.header("🗂️ Database")
    st.write("On this page, you'll find a list of all the databases you've created after uploading folders and naming them. You have the option to remove any folder as needed.")

# Accurate Search section
expander = st.expander("🔍 Accurate Search")

with expander:
    # st.header("🔍 Accurate Search")
    st.write("When opting for the accurate search feature, InfoHunter scans your documents and compares your query to the most relevant documents, providing a precise match for your search request.")
    st.write("InfoHunter can provide up to 10 documents that match your query, ranking them in order of similarity, from the most closely related to the least similar.")
    st.write("Additionally, InfoHunter supplies the precise location of each document, ensuring a convenient and seamless user experience.")


# Chatbot section
expander = st.expander("🤖 Chatbot")

with expander:
    # st.header("🤖 Chatbot")
    st.write("Using the chatbot feature, you can engage in conversation with your documents through the advanced language capabilities of ChatGPT 3.5.")
    st.write("The chatbot feature also includes a memory function that retains the history of your prior interactions with the chatbot for a more coherent and contextual conversation.")