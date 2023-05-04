import streamlit as st
import os
import pandas as pd

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAI
from langchain.chains import RetrievalQA
from utilities import load_database_self, db_folder


st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")

if "API_key" not in st.session_state:
    st.session_state["API_key"] = ""
if "API_key_valid" not in st.session_state:
    st.session_state["API_key_valid"] = False
if "query" not in st.session_state:
    st.session_state["query"] = ""
if "answer" not in st.session_state:
    st.session_state["answer"] = ""


@st.cache(allow_output_mutation=True)
def get_answer_docs(query, index_path, k):
    embeddings = OpenAIEmbeddings(openai_api_key=st.session_state["API_key"])
    vectordb = Chroma(persist_directory=index_path, embedding_function=embeddings)
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(openai_api_key=st.session_state["API_key"],temperature=0),
        chain_type='stuff',
        retriever=vectordb.as_retriever(search_kwargs={"k":k})
    )
    answer = qa.run(query)
    similar_docs = vectordb.similarity_search_with_score(query,k=k)

    return answer, similar_docs


st.header("Accurate Search")
st.subheader("Accurate search in selected index")

record_self = load_database_self()
options = list(record_self.Index.values)
st.markdown("Select an index")
selected_index = st.selectbox("Select an index", options, label_visibility="collapsed")

if selected_index is not None:  
    index_path = os.path.join(os.getcwd(), db_folder, selected_index)
    if not st.session_state["API_key_valid"]:
        st.error("Please validate your API key at Homepage")
    else:        
        query = st.text_input("Input your query")
        st.write("- The default number of related documents to retrieve (k number) is 4 or 1, depending on vector counts in the index")
        st.write("- Or you can:")
        define_k = st.checkbox("Set your desired k number (limited by vector counts)")
        
        n_vectors = record_self.loc[record_self.Index==selected_index, "vector counts"].squeeze()
        valid_k = False
        if not define_k :
            if n_vectors > 6:
                k = 4
            else:
                k = 1
            valid_k = True
        else:
            input_k = st.text_input("Set k number:")
            if not input_k.isdigit():
                st.error(f"Please input an integer no higher than {n_vectors}")
            elif int(input_k) > n_vectors:
                st.error(f"Please input an integer no higher than {n_vectors}")
            else:
                k = int(input_k)
                valid_k = True

        submit_query = st.button("Submit query")
        st.write("---")

        if ((len(query) == 0) & submit_query):
            st.error("Please give a query") 
        elif (valid_k & submit_query):
            with st.spinner("......"):
                st.session_state["query"] = query
                st.session_state["k"] = k
                answer, similar_docs = get_answer_docs(query, index_path, k)
                st.session_state["answer"] = answer
                st.session_state["similar_docs"] = similar_docs
                
                st.write("##")                    
                
                st.spinner("") # clear spinner

not_found = ["not found", "don't know", "do not know", "not find", "n't find", "not be found", "n't be found"]
if len(st.session_state["answer"])>0:
    st.write("**Query**:", st.session_state["query"])
    st.write("**Answer**:", st.session_state["answer"])
    st.write("##")

    if any(_ in st.session_state["answer"] for _ in not_found):
        st.write("The query is out of the scope of the documents in your selected index")
    else:
        explain_score = "(a lower **distance score** indicates a higher level of relevance)"
        if st.session_state['k'] == 1:
            st.write(f"**Top {st.session_state['k']} related document:** {explain_score}")
        else:
            st.write(f"**Top {st.session_state['k']} related documents:** {explain_score}")

        for i in range(st.session_state['k']):
            st.markdown(f"-- **#{i+1}** --")
            st.markdown(f"**Document Location**: {st.session_state['similar_docs'][i][0].metadata}")
            st.markdown(f"**Distance Score**: {st.session_state['similar_docs'][i][1]:.3f}")
            if st.checkbox("Display document content"):
                st.markdown(st.session_state['similar_docs'][i][0].page_content)