from bertopic import BERTopic
from bertopic.backend._utils import select_backend
import streamlit as st
from process_scripts import preprocess, get_speakers
from visualize import plot_speakers
from visualize_topics import get_intertopic_distance_map
from sentence_transformers import SentenceTransformer

sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
model = select_backend(sentence_model)
# remove embedding model from topic model so it can be loaded without GPU
# (https://github.com/MaartenGr/BERTopic/issues/165)
topic_model = BERTopic.load("best_model", embedding_model=model)

# topic_model = BERTopic.load('news_topic_model')

with st.form('file'):
    file = st.file_uploader("Upload a script or transcript")  # TODO handle multiple files
    # checkboxes for different tasks
    checkbox_row = st.columns(3)
    checkboxes = {}
    with checkbox_row[0]:
        checkboxes["Sectionizing"] = st.checkbox("Sectionizing")
    with checkbox_row[1]:
        checkboxes["Vector representations"] = st.checkbox("Vector representations")
    with checkbox_row[2]:
        checkboxes["Topic modeling"] = st.checkbox("Topic modeling")
    upload = st.form_submit_button("Upload")
    if upload:
        # preprocessing
        # if sectionizing: do processing for each act
        lines = preprocess(file)
        st.write(lines)
        speakers = get_speakers(lines)
        # save to database
        # modeling
        if checkboxes["Vector representations"]:
            vector_visualization = plot_speakers(speakers)
            # plot_speakers(topic_model, speakers)
        if checkboxes["Topic modeling"]:
            intertopic_distance_map = get_intertopic_distance_map('\n'.join(lines), topic_model)
            st.write(intertopic_distance_map)
