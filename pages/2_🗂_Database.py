import streamlit as st
import os
import shutil
import pandas as pd
from utilities import load_database_self, record_path, db_folder

st.set_page_config(
    page_title="InfoHunter",
    layout="wide"
)

st.sidebar.success("Select a page above")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)


record_self = load_database_self()
record_self_ = record_self.drop("vector counts", axis=1)
st.subheader("Database")
table = st.table(record_self_)
st.write("##")

# Discard this function
# Do not encourage personal users to share indice; enterprise users can share indice from cloud
# st.subtitle("Transfer index database from other users")
# st.subheader("(Enterprise users can generate multiple databases and share on cloud)")
# st.write("##")

st.markdown("**Delete obsolete database**")
# st.markdown("Although this function allows to delete an index from your index database, this is <span style='color:red'>not recommended</span>.", unsafe_allow_html=True)
# st.write("(can implement user id and password to secure)")
index2delete = st.text_input("Enter database to delete (e.g., idx_notes1)")
if len(index2delete) > 0:
    if index2delete not in record_self.Index.values:
        st.error(f"Index {index2delete} does not exist")
    else:
        confirm_delete = st.checkbox(f"Confirm to delete {index2delete}")
        if confirm_delete:
            delete = st.button("Delete Index")
            if delete:
                delete_path = os.path.join(os.getcwd(), db_folder, index2delete)
                shutil.rmtree(delete_path)
                record_self = record_self.drop(record_self[record_self.Index==index2delete].index).reset_index(drop=True)
                record_self.to_csv(record_path, index=False)
                table.dataframe(record_self)
