import streamlit as st
import requests
from PIL import Image


st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")

folder2database_img = Image.open("images/folder2database2.png")

def local_css(file_name):
    """
    This function defines the format of st.write and st.markdown
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css") 
# Use the format defined in style.css for subsequent st.write and st.markdown until another style is given to local_css


# Page Title
st.title("InfoHunter: Your Personal Assistant for Document Search")

# What is infoHunter section
expander = st.expander("🤔 What is InfoHunter?")

with expander:
    # Page header
    st.write("<p style='font-size: 20px; font-weight: bold;'>Description</p>", unsafe_allow_html=True)

    # Description of InfoHunter
    st.write("InfoHunter, powered by GPT 3.5, serves as a personal assistant for document search. This tool enables swift access to your individual notes and provides the capability to interact with them through conversation.")

    # Features section
    st.write("<p style='font-size: 20px; font-weight: bold;'>Features</p>", unsafe_allow_html=True)
    st.write("InfoHunter offers two primary features:")
    st.write("- Precise searching within your documents (Accurate Search)")
    st.write("- Interactive communication with your files (Chatbot)")
    st.write("")

    # Instructions section
    left_column, image_column = st.columns((2,1))
    with left_column:
        st.write("<p style='font-size: 20px; font-weight: bold;'>Instructions</p>", unsafe_allow_html=True)
        st.write("To use InfoHunter, follow these simple steps: 👍🏼")
        st.write("1. Create an OpenAI API key")
        st.write("2. Enter your document folder path")
        st.write("3. Name a database to hold your document embeddings")
        st.write("4. Select Accurate Search/Chatbot")
        st.write("5. Enter your queries")
    with image_column:
        st.write("##")
        st.write("##")
        st.write("##")
        st.image(folder2database_img)

# Homepage section
expander = st.expander("🏠 Homepage")

with expander:

    # st.subheader("🏠 Homepage")

    # Register OpenAI account and generate API key
    st.write("Prior to using InfoHunter, you will need to register an OpenAI account and generate an API key here: https://platform.openai.com/account/api-keys")
    st.write("An OpenAI API key is a unique identifier provided by OpenAI. This key allows you to access and use OpenAI's large language models. It is essential to keep your key secure, as it grants access to your account and usage of the services, which is subject to usage limits or costs.")

# Create Database section
expander = st.expander("📝 Create Database")
with expander:

    # st.header("📝 Create Database")
    st.write("1. Specify a folder path where you’d like to utilize InfoHunter for document \
            interaction (e.g., your study notes, work notes, daily records). ")

    st.info("**Absolute** path to your **folder** is required. Examples: \n\n " 
            "Mac user: /Users/username/Documents/study_notes \n\n" 
            "Windows user: C:\\Users\\username\\Documents\\work_files")

    st.write("2. Assign a name to your document database (e.g., note1)")
    st.write("3. Once you click 'submit,' InfoHunter will transform your documents into embeddings and store them in a database for further use.")

    # Supported document formats section
    st.warning("The supported document formats for InfoHunter are: \n\n" \
            "Microsoft Word (.docx), Microsoft Excel (.xlsx), Microsoft PowerPoint (.pptx) \n\n" 
            "Apache OpenOffice Text (.odt), Apache OpenOffice Spreadsheet (.ods) \n\n"
            "Portable Document Format (.pdf), Plain text (.txt), Web page (.html) \n\n"
            "Jupyter Notebook (.ipynb), Python script (.py)")

# Database section
expander = st.expander("🗂️ Database")

with expander:
    # st.header("🗂️ Database")
    st.write("On this page, you'll find a list of all the databases you've created. You have the option to remove any database as needed.")

# Accurate Search section
expander = st.expander("🔍 Accurate Search")

with expander:
    # st.header("🔍 Accurate Search")
    st.write("When opting for the accurate search feature, InfoHunter scans your documents and compares your query to the most relevant documents, providing a close match for your search request.")
    st.write("InfoHunter can provide up to 10 most relevant document sections to your query, ranking them in order of similarity.")
    st.write("Additionally, InfoHunter supplies the precise location of each document section, ensuring a convenient and seamless user experience.")


# Chatbot section
expander = st.expander("🤖 Chatbot")

with expander:
    # st.header("🤖 Chatbot")
    st.write("Using the chatbot feature, you can engage in conversation with your documents through the advanced language capabilities of GPT 3.5.")
    st.write("The chatbot feature also includes a memory function that retains the history of your prior interactions with the chatbot for a more coherent and contextual conversation.")