import os
import sqlite3
import streamlit as st

from bertopic import BERTopic
from bertopic.backend._utils import select_backend
from sentence_transformers import SentenceTransformer

from process_scripts import preprocess, get_speakers
from visualize import plot_speakers
from database import TopicDatabase

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
conn = create_connection(db_file)
db = TopicDatabase(conn)


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

        # modeling
        if checkboxes["Vector representations"]:
            vector_visualization = plot_speakers(sentence_model, speakers)
            st.pyplot(vector_visualization)
        if checkboxes["Topic modeling"]:
            # save to database
            db.add_file(file.name, lines)
            for speaker_name, items in speakers.items():
                sentences = [item[-1] for item in items]
                db.update_speaker(speaker_name, sentences)
                topics, _ = topic_model.transform(sentences)
                for topic_id in topics:
                    topic_name = topic_model.get_topic_info(topic_id).Name[0]
                    # remove index prefix
                    _, topic_name = topic_name.split("_", maxsplit=1)
                    db.add_topic(int(topic_id), topic_name, speaker_name)
            st.write(topic_model.visualize_topics())

db.close()
