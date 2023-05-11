import streamlit as st
import pandas as pd
from visualize import plot_speakers

st.set_page_config(page_title="Visualization")

# checkboxes for speaker names
st.session_state.selected = st.radio("Choose a character to view in more detail:",
                                     tuple(st.session_state.all_speakers))
speaker_name = st.session_state.selected
speaker_development = {}
for i, section in enumerate(st.session_state.sections):
    speaker_development[speaker_name + str(i)] = section[speaker_name]

# visualize vectors
if st.session_state.visualize_vectors:
    vector_visualization = plot_speakers(st.session_state.sentence_model,
                                         speaker_development)

# visualize topics
if st.session_state.visualize_topics:
    st.write("Speaker topics")
    topics = st.session_state.db.get_topics_by_speaker()
    # get topic name, count, and speaker name
    data = [[topic[1], topic[3], topic[5]] for topic in topics
            if topic[5] in speaker_development]
    df = pd.DataFrame(data, columns=["Topic", "Count", "Speaker"])
    st.dataframe(df)
