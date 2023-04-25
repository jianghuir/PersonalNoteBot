import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.retrieval import RetrievalQA
from langchain import OpenAI
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain import OpenAI
import os
import glob
import nbformat
from nbconvert import PythonExporter
from PyPDF2 import PdfReader
import subprocess  
import pandas as pd
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA
from langchain.document_loaders import DirectoryLoader
import nltk

# Include the updated get_documents function here
def get_documents(folder_path):
    '''
    This function reads all files in a folder, 
    converts 10 file types into langchain.docstore.document.Document objects
    return: [Document objects]
    '''   
    
    documents = []
    # Loop through files in the folder
    for file_name in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file_name)
        print(file_path)
        file_extension = os.path.splitext(file_name)[1]
        content = None
        content_sheets = None
        data = None
        pages = None
        doc = None

        if file_extension in {'.txt', '.pdf', '.odt', '.ods', '.docx', '.xlsx', '.ipynb', '.py', '.pptx', 'html'}:

            # Read the file based on its extension
            if file_extension == '.pdf':
                print("this is a pdf")
                loader = PyPDFLoader(file_path)
                pages = loader.load_and_split() # a list of Document objects, separate by page

            elif file_extension == '.docx':
                print("this is a docx")
                loader = UnstructuredWordDocumentLoader(file_path)
                data = loader.load() # a list of one Document object

            elif file_extension == '.pptx':
                print("this is a pptx")
                loader = UnstructuredPowerPointLoader(file_path)
                data = loader.load() # a list of one Document object

            elif file_extension == '.html':
                print("this is a html")
                loader = UnstructuredHTMLLoader(file_path)
                data = loader.load() # a list of one Document object

            elif file_extension in ('.txt', '.py'):
                print("this is a txt or py")
                from langchain.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding='utf8')
                data = loader.load() # a list of one Document object

            elif file_extension == '.odt':
                print("this is a odt")
                cmd = ['unoconv', '--stdout', '-f', 'txt', file_path]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                content = stdout.decode('utf-8') # a string

            elif file_extension == '.ipynb':
                print("this is a ipynb")
                with open(file_path, 'r', encoding='utf-8') as f:
                    notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)
                exporter = PythonExporter()
                content, _ = exporter.from_notebook_node(notebook) # content is a string            

            elif file_extension in ('.ods', '.xlsx'):
                print("this is a ods or xlsx")
                excel_file = pd.ExcelFile(file_path)
                # Iterate over sheets and extract data
                content_sheets = {}
                for sheet_name in excel_file.sheet_names:
                    content_sheets[sheet_name] = excel_file.parse(sheet_name) 
                    # each sheet is saved as a DataFrame

            else:
                pass


            # save each file as a Document object or Document objects
            # append Document into "documents" list
            if data:
                print(file_path, "has data.")
                documents += data

            elif pages:
                print(file_path, "has pages.")
                documents += pages

            elif content:
                print(file_path, "has content.")
                content = content.replace("  ","")
                doc = Document(page_content=content, metadata={"source": file_path})
                documents.append(doc)

            elif content_sheets:
                print(file_path, "has content_sheets.")
                for sheet_name in content_sheets:
                    content_in_sheet = str(content_sheets[sheet_name])
                    # remove large amounts of space and NaN in xlsx and ods
                    content_in_sheet = content_in_sheet.replace("  ","")
                    content_in_sheet = content_in_sheet.replace("NaN", "")
                    doc = Document(page_content=content_in_sheet, metadata={"source": file_path, "sheet": sheet_name})
                    documents.append(doc)

            else:
                pass
            
    return documents



# UI Elements
st.title("Document Search and QA")
folder_path = st.text_input("Enter the folder path containing your documents:", "")

if folder_path:
    documents = get_documents(folder_path)
    st.write(f"Number of documents: {len(documents)}")

    # Split each document into a good size
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_documents = text_splitter.split_documents(documents)

    # Define embedding
    os.environ["OPENAI_API_KEY"] = "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"
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    # Save and load embeddings
    persist_directory = 'db2'
    vectordb = Chroma.from_documents(documents=split_documents, embedding=embeddings, persist_directory=persist_directory)
    vectordb.persist()
    vectordb = None
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    st.success("Embeddings saved to and loaded from local directory 'db2' successfully.")

    # Chatbot QA function
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type='stuff', retriever=vectordb.as_retriever())

    # Add a text input for the user to enter a query
    query = st.text_input("Enter your query:", "")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = ""

    if query:
        st.session_state.conversation_history += f"User: {query}\n"

        response = qa.run(query)
        st.session_state.conversation_history += f"Assistant: {response}\n"

        st.write("Conversation history:")
        st.write(st.session_state.conversation_history)

        # Similarity search to return related documents
        similar_docs = vectordb.similarity_search_with_score(query)

        # Display the similar documents
        st.write("Similar documents:")

        for doc, score in similar_docs:
            st.write(f"Score: {score:.2f}")
            st.write("Document content:")
            st.write(doc.page_content)
