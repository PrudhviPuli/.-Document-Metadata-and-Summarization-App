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