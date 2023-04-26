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

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain import OpenAI
from langchain.chains import RetrievalQA

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def read_file(file_path):
    '''
    This function reads a file among eligible file types:
         {'.txt', '.pdf', '.odt', '.ods', '.docx', '.xlsx', '.ipynb', '.py', '.pptx', '.html'},
    and converts the file into langchain.docstore.document.Document object
    return: [Document(s)]
    '''       

    content, content_sheets, data, pages, doc = None, None, None, None, None

    file_extension = os.path.splitext(file_path)[1]
    
    if file_extension in {'.txt', '.pdf', '.odt', '.ods', '.docx', '.xlsx', '.ipynb', '.py', '.pptx', '.html'}:

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


        # save the file as a Document object
        if data:
            print(file_path, "has data.")
            return data

        elif pages:
            print(file_path, "has pages.")
            return pages

        elif content:
            print(file_path, "has content.")
            content = content.replace("  ","")
            doc = Document(page_content=content, metadata={"source": file_path})
            return [doc]

        elif content_sheets:
            print(file_path, "has content_sheets.")
            docs = []
            for sheet_name in content_sheets:
                content_in_sheet = str(content_sheets[sheet_name])
                # remove large amounts of space and NaN in xlsx and ods
                content_in_sheet = content_in_sheet.replace("  ","")
                content_in_sheet = content_in_sheet.replace("NaN", "")
                sheet = Document(page_content=content_in_sheet, metadata={"source": file_path, "sheet": sheet_name})
                docs.append(sheet)
            return docs

        else:
            pass

    return []


def folder_recursion(folder_path):
    """
    This function loops through the contents in a root folder:
    if a content is a single file, run read_file();
    if a content is a foler, recurse folder_recursion().
    return: [Documents], all eligible document types in the root folder and all subfolders
    """

    documents = []
    
    # Loop through files in the folder
    for file_name in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isdir(file_path): # file_path is a folder
            documents += folder_recursion(file_path)
        
        else: # file_path is a single file
            documents += read_file(file_path)
    
    return documents


# read all files in folder_path, including files in subfolders
folder_path = 'notes3/' #the folder directory containing your notes
documents = folder_recursion(folder_path)
print(f"Read in {len(documents)} documents (and pages) from directory {folder_path}")

# split each document into a good size
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_documents = text_splitter.split_documents(documents)
len(split_documents)

os.environ["OPENAI_API_KEY"] = "you key"
embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

# attention: we need persist_directory to save our embeddings for later use
# OpenAI charges on embedding and run(query)
# a folder named 'db' is created inside folder_path, db has your embeddings
persist_directory = 'db3'
vectordb = Chroma.from_documents(documents=split_documents, embedding=embeddings, persist_directory=persist_directory)
#vectordb.persist() # need .persist() in ipynb to save to local drive. in python script, this is automatic
# vectordb = None
# vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings) # successfully load embedding from local
