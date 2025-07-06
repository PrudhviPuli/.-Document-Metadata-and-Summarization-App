import streamlit as st
import requests
import base64
import pandas as pd

API_BASE_URL = "https://83e38bczul.execute-api.us-east-1.amazonaws.com/production"

st.title("Document Uploader & Viewer")

# Upload Section
st.subheader("Upload Document")
uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])

if uploaded_file is not None:
    file_content = uploaded_file.read()
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    filename = uploaded_file.name
    
    if st.button("Upload to Server"):
        response = requests.post(
            f"{API_BASE_URL}/upload",
            json={
                "filename": filename,
                "file_content": encoded_content
            }
        )
        if response.status_code == 200:
            st.success("File uploaded successfully!")
        else:
            st.error(f"Failed to upload: {response.text}")

# Document List Section
st.subheader("List of Uploaded Documents")
if st.button("Fetch Documents List"):
    response = requests.get(f"{API_BASE_URL}/documents")
    if response.status_code == 200:
        docs = response.json()
        if docs:
            st.dataframe(pd.DataFrame(docs))
        else:
            st.info("No documents found.")
    else:
        st.error(f"Failed to fetch documents: {response.text}")