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

# Summary Section - Always visible
st.subheader("🔍 Summarize a Document")
if st.session_state.documents_df is not None and not st.session_state.documents_df.empty:
    selected_doc = st.selectbox(
        "Select document",
        st.session_state.documents_df['Filename'].unique(),
        key="doc_selector"
    )
    
    if st.button("✨ Generate Summary", type="primary"):
        selected_row = st.session_state.documents_df[
            st.session_state.documents_df['Filename'] == selected_doc
        ].iloc[0]
        
        with st.spinner("Generating summary..."):
            try:
                sum_response = requests.get(
                    f"{API_URL}/summarize/{selected_row['DocumentId']}",
                    params={"uploadDate": selected_row['UploadDate']}
                )
                
                if sum_response.status_code == 200:
                    result = sum_response.json()
                    st.success("📝 Summary:")
                    st.markdown(result['summary'])
                    
                    with st.expander("View Metadata"):
                        st.json({
                            "Filename": selected_row['Filename'],
                            "Size": int(selected_row['Size']),
                            "UploadDate": selected_row['UploadDate'],
                            "DocumentId": selected_row['DocumentId']
                        })
                else:
                    st.error(f"❌ Failed to summarize: {response.text}")
            except Exception as e:
                st.error(f"🚨 Error during summarization: {str(e)}")
else:
    st.info("ℹ️ No documents available. Please upload or refresh documents.")