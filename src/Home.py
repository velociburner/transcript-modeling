import os
import sqlite3
import streamlit as st

from bertopic import BERTopic
from bertopic.backend._utils import select_backend
from visualize_topics import get_intertopic_distance_map
from sentence_transformers import SentenceTransformer

from process_scripts import preprocess, get_speakers
from visualize import plot_speakers
from database import add_file, create_tables, update_speaker

sentence_model = SentenceTransformer("all-MiniLM-L12-v2")
model = select_backend(sentence_model)
# remove embedding model from topic model so it can be loaded without GPU
# (https://github.com/MaartenGr/BERTopic/issues/165)
topic_model = BERTopic.load("best_model", embedding_model=model)


def create_connection(db_file):
    db = None

    try:
        db = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        st.write(f"Error: {e}")

    return db


db_file = os.path.join("instance", "transcripts.db")
db = create_connection(db_file)
create_tables(db)


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
        add_file(db, file.name, lines)
        for name, sentences in speakers.items():
            update_speaker(db, name, sentences)
        # modeling
        if checkboxes["Vector representations"]:
            vector_visualization = plot_speakers(topic_model, speakers)
            # plot_speakers(topic_model, speakers)
        if checkboxes["Topic modeling"]:
            intertopic_distance_map = get_intertopic_distance_map('\n'.join(lines), topic_model)
            st.write(intertopic_distance_map)
