import os
import sqlite3
import streamlit as st


from bertopic import BERTopic
from bertopic.backend._utils import select_backend
from sentence_transformers import SentenceTransformer


from process_scripts import preprocess, get_speakers
from sectionize import sectionize_play
from visualize import plot_speakers
from database import TopicDatabase

st.set_page_config(page_title="Home")

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


if 'sections' not in st.session_state:  # setting up sections of a transcript
    st.session_state.sections = []
st.session_state.sentence_model = sentence_model
st.session_state.topic_model = topic_model
st.session_state.visualize_vectors = False
st.session_state.visualize_topics = False

with st.form('file'):
    file = st.file_uploader("Upload a script or transcript")  # TODO handle multiple files
    # checkboxes for different tasks
    checkbox_row_1 = st.columns(2)
    checkboxes = {}

    with checkbox_row_1[0]:  # split document into different sections (typically acts)
        checkboxes["Sectionize"] = st.checkbox("Sectionize")
    with checkbox_row_1[1]:
        checkboxes["Print processed lines"] = st.checkbox("Print processed lines")
    checkbox_row_2 = st.columns(2)
    with checkbox_row_2[2]:  # get vector representations for each speaker's dialogue
        checkboxes["Vector representations"] = st.checkbox("Vector representations", value=True)
    with checkbox_row_2[3]:
        checkboxes["Topic modeling"] = st.checkbox("Topic modeling", value=True)
    upload = st.form_submit_button("Upload")
    if upload:
        st.write("Wait for it...")
        # preprocessing
        text = file.read().decode('utf-8')
        if checkboxes["Sectionize"]:
            sections = sectionize_play(text)
            sections = [section.text for section in sections if section.category in ["Act", "Scene", "Speech"]]
        else:
            sections = [text]
        
        db.add_file(file.name, '\n'.join(sections))

        # if sectionizing: do processing for each act
        for i, section in enumerate(sections):
            lines = preprocess(section)
            speakers = get_speakers(lines)
            # save to database
            db.add_file(file.name + '_' + str(i), lines)
            if checkboxes["Print processed lines"]:
                st.write(lines)
            st.session_state.sections.append(speakers)

        # modeling
        if checkboxes["Vector representations"]:  # generate vector representations
            # this is handled in teh visualization pages
            st.session_state.visualize_vectors = True

        if checkboxes["Topic modeling"]:  # model topics
            st.session_state.visualize_topics = True
            # save to database
            for speaker_name, items in speakers.items():
                sentences = [item[-1] for item in items]
                db.update_speaker(speaker_name, sentences)
                topics, _ = topic_model.transform(sentences)
                for topic_id in topics:
                    topic_name = topic_model.get_topic_info(topic_id).Name[0]
                    # remove index prefix
                    _, topic_name = topic_name.split("_", maxsplit=1)
                    db.add_topic(int(topic_id), topic_name, speaker_name)
                    # st.write(topic_model.visualize_topics())

        st.write("Done preprocessing! Click \"visualize entire script\" on the left to see results.")
                
                

db.close()
