# from bertopic import BERTopic
import streamlit as st
from consolidate_lines_txt import preprocess
from placeholder import get_intertopic_distance_map

# topic_model = BERTopic.load('news_topic_model')

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
        print(file)
        text = preprocess(file)
        st.write(text)
        # save to database
        # modeling
        if checkboxes["Vector representations"]:
            pass
        if checkboxes["Topic modeling"]:
            pass
            # intertopic_distance_map = get_intertopic_distance_map(text, topic_model)
            # st.write(intertopic_distance_map)
        pass

