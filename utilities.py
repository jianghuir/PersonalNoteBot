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
import streamlit as st


record_path = os.path.join(os.getcwd(),"database_record_self.csv")
db_folder = "Index_Database_self/"

def update_database_record(index_name, original_docs, num_vectors):
    """
    This function updates "database_record_self.csv" in cwd
    This csv file tracks indices in cwd/db_folder
    """
    
    if not os.path.exists(record_path):
        # if database_record_self.csv doesn't exist, create one
        record = pd.DataFrame({"Index": index_name, "vector counts": int(num_vectors), "Documents": str(original_docs)}, index=[0])
    
    else: # database_record_self.csv exist
        record = pd.read_csv(record_path)

        # if an index folder is deleted by user, update record
        for idx in record.Index.values:
            idx_path = os.path.join(os.getcwd(), db_folder, idx)
            if not os.path.isdir(idx_path):
                record = record.drop(record[record.Index==idx].index)
        
        if index_name not in record.Index.values:
            # if index_name is new, append it to record
            new_row = pd.DataFrame({"Index": index_name, "vector counts": int(num_vectors), "Documents": str(original_docs)}, index=[0])
            record = pd.concat([record,new_row], ignore_index=True)
        else:
            # if index_name is existing, replace the existing index in record
            record.loc[record.Index==index_name, "Documents"] = str(original_docs)
            record.loc[record.Index==index_name, "vector counts"] = int(num_vectors)
    # save database_record_self.csv
    record.to_csv(record_path, index=False)
    return


def load_database_self():
    """
    This function loads and displays "database_record_self.csv" in cwd to app
    """
    if not os.path.exists(record_path):
        # if database_record_self.csv doesn't exist, create one
        record = pd.DataFrame(columns=['Index', 'Documents'])
        record.to_csv(record_path, index=False)
    
    else: # database_record_self.csv exist
        record = pd.read_csv(record_path)
        need_update = False
        # if an index folder is deleted by user, update record
        for idx in record.Index.values:
            idx_path = os.path.join(os.getcwd(), db_folder, idx) 
            if not os.path.isdir(idx_path):
                need_update = True
                record = record.drop(record[record.Index==idx].index)
        if need_update:
            record.to_csv(record_path, index=False)       
    
    record["vector counts"] = record["vector counts"].astype(int)
    record = record.reset_index(drop=True)
    record.index += 1
    return record


def read_file(file_path):
    '''
    This function reads a file among eligible file types:
         {'.txt', '.pdf', '.odt', '.ods', '.docx', '.xlsx', '.ipynb', '.py', '.pptx', '.html'},
    and converts the file into langchain.docstore.document.Document object
    return: [Document(s)]
    '''       

    content, content_sheets, data, pages, doc = None, None, None, None, None
    
    file_extension = os.path.splitext(file_path)[1]
    st.write("8")
    if file_extension in {'.txt', '.pdf', '.odt', '.ods', '.docx', '.xlsx', '.ipynb', '.py', '.pptx', '.html'}:

        # Read the file based on its extension
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split() # a list of Document objects, separate by page

        elif file_extension == '.docx':
            loader = UnstructuredWordDocumentLoader(file_path)
            data = loader.load() # a list of one Document object

        elif file_extension == '.pptx':
            loader = UnstructuredPowerPointLoader(file_path)
            data = loader.load() # a list of one Document object

        elif file_extension == '.html':
            loader = UnstructuredHTMLLoader(file_path)
            data = loader.load() # a list of one Document object

        elif file_extension in ('.txt', '.py'):
            loader = TextLoader(file_path, encoding='utf8')
            data = loader.load() # a list of one Document object

        elif file_extension == '.odt':
            cmd = ['unoconv', '--stdout', '-f', 'txt', file_path]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            content = stdout.decode('utf-8') # a string

        elif file_extension == '.ipynb':
            #st.write("9")
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)
                #st.write("10")
            exporter = PythonExporter()            
            content, _ = exporter.from_notebook_node(notebook) # content is a string          

        elif file_extension in ('.ods', '.xlsx'):
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
            st.write(file_path, "has data.")
            return data, [file_path]

        elif pages:
            st.write(file_path, "has pages.")
            return pages, [file_path]

        elif content:
            #st.write(file_path, "has content.")
            content = content.replace("  ","")
            doc = Document(page_content=content, metadata={"source": file_path})
            #st.write("1")
            return [doc], [file_path]

        elif content_sheets:
            #st.write(file_path, "has content_sheets.")
            docs = []
            for sheet_name in content_sheets:
                content_in_sheet = str(content_sheets[sheet_name])
                # remove large amounts of space and NaN in xlsx and ods
                content_in_sheet = content_in_sheet.replace("  ","")
                content_in_sheet = content_in_sheet.replace("NaN", "")
                sheet = Document(page_content=content_in_sheet, metadata={"source": file_path, "sheet": sheet_name})
                docs.append(sheet)
            return docs, [file_path]

        else:
            pass

    return [], []


def folder_recursion(folder_path):
    """
    This function loops through the contents in a root folder:
    if a content is a single file, run read_file();
    if a content is a foler, recurse folder_recursion().
    return: [Documents], all eligible document types in the root folder and all subfolders,
            and original_doc, all eligible original documents
    """

    documents = []
    original_docs = []
    # Loop through files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.startswith((".", "~")):# ignore hidden files and temp files
            #st.write(f"ignore {file_name}")
            pass
        else:
            #st.write(file_path)
            try:
                if os.path.isdir(file_path): # file_path is a folder
                    #st.write("6")
                    results = folder_recursion(file_path)
                    documents += results[0]
                    original_docs += results[1]
                    #st.write("2")
                else: # file_path is a single file
                    #st.write("7")
                    results = read_file(file_path)
                    documents += results[0]
                    original_docs += results[1]
                    #st.write("3")
        
            except Exception as e:
                st.error(e)
                if isinstance(e, IndentationError):
                    st.error(f"To locate the indentation error: Please search the phrase **'{e.args[1][-1]}'** in {file_path}. Click 'Submit' again after you fix the indentation or remove the errored file.")
    
    return documents, original_docs   

