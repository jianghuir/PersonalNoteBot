import streamlit as st
import os
import nbformat
from nbconvert import PythonExporter
import subprocess  
import pandas as pd

from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from utilities import update_database_record, folder_recursion, db_folder

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAI
from langchain.chains import RetrievalQA
from PIL import Image

st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")

if "API_key" not in st.session_state:
    st.session_state["API_key"] = ""
if "API_key_valid" not in st.session_state:
    st.session_state["API_key_valid"] = False



pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

img_folder = Image.open("images/folder.png")

def create_index_from_folder(folder_path, index_name, API_key):
    """
    read all files in folder_path (including files in subfolders), convert to vector index and save in database
    folder_path: the folder directory of files to convert
    index_name: database name defined by user
    """ 
    documents, original_docs = folder_recursion(folder_path)
    #st.write(f"Read in {len(documents)} documents (and pages/sheets) from directory {folder_path}")

    # split each document into a good size
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_documents = text_splitter.split_documents(documents)
    num_vectors = len(split_documents)

    embeddings = OpenAIEmbeddings(openai_api_key=API_key)

    # attention: we need persist_directory to save our embeddings for later use
    # OpenAI charges on embedding and run(query)
    # a folder named index_name is created inside cwd
    
    
    index_path = os.path.join(os.getcwd(), db_folder, index_name)
    Chroma.from_documents(documents=split_documents, embedding=embeddings, persist_directory=index_path)

    st.success(f"Eligible files in folder {folder_path} are successfully indexed and saved in index database")

    # update database_record_self.csv
    update_database_record(index_name, original_docs, num_vectors)

    return




with st.container():
    st.write("##")
    st.write("##")
    st.subheader("Select a folder of files for indexing")

    left_column, image_column1 = st.columns((4,1))
    

    with left_column:
        valid_folder, valid_index, replace_index, index_folder = False, False, False, False
        st.write("**All eligible files in the folder and its subfolders are indexed and saved in Index Database**")
        folder_path = st.text_input("Folder Directory (please input an absolute path)")
        if folder_path: # check if the folder directory is valid            
            if len(folder_path) == 0:
                valid_folder = False
                st.write("You need to provide the absolute path of your folder for indexing")
            elif not os.path.isdir(folder_path):
                valid_folder = False
                st.error("The folder directory is invalid")
            else:
                valid_folder = True

        index_name = st.text_input("Index name: Please name your index, e.g., idx_notes1")
        
        if index_name: # check if database name is pre-existing
            if len(index_name) == 0:
                valid_index = False
                st.write("You need to name your index")
            elif os.path.isdir(os.path.join(os.getcwd(), db_folder, index_name)):
                valid_index = False
                st.write("This index name is existing:")
                st.markdown("- If you do <span style='color:red'>NOT</span> want to replace the existing index, <span style='color:red'>give a unique name in 'Index name'</span>.", unsafe_allow_html=True)
                st.write("- If you DO want to replace, check **REPLACE**:")
                replace_index = st.checkbox("I want to REPLACE existing index")
                st.write("##")
            else:
                valid_index = True

            if replace_index:
                valid_index = True

        index_folder = st.button("📋 Index documents")
        
        if index_folder:
            if not st.session_state["API_key_valid"]:
                st.error("Please validate your API key at Homepage.")
            if not valid_folder:
                st.error("The folder directory is invalid. Please provide an absolute path to the folder.")
            if not valid_index:
                st.error("You need to either provide a unique index name or check **REPLACE**")
            if st.session_state["API_key_valid"] and valid_folder and valid_index:
                with st.spinner("Indexing documents..."):
                    create_index_from_folder(folder_path=folder_path, index_name=index_name, API_key=st.session_state["API_key"])
                    st.spinner("") # clear spinner


    with image_column1:
        st.image(img_folder)






