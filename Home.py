import streamlit as st

with st.form('file'):
    file = st.file_uploader("Upload a script or transcript")  # TODO handle multiple files
    # TODO checkboxes for different tasks
    checkbox_row = st.columns(2)
    checkboxes = {}
    with checkbox_row[0]:
        checkboxes["Vector representations"] = st.checkbox("Vector representations")
    with checkbox_row[0]:
        checkboxes["Topic modeling"] = st.checkbox("Topic modeling")
    upload = st.form_submit_button("Upload")
    if upload:
        # preprocessing
        # save to database
        # modeling
        if checkboxes["Vector representations"]:
            pass
        if checkboxes["Topic modeling"]:
            pass
        pass

