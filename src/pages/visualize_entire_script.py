# visualize vector representations and topics for all speakers in a script
# users can select a speaker to see that speaker's individual visualization (visualize_singlespeaker.py)
import streamlit as st
import pandas as pd
from visualize import plot_speakers

st.set_page_config(page_title="Visualization")

all_speakers = {}
for section in st.session_state.sections:
    all_speakers.update(section)  # get all speaker names from this section
st.session_state.all_speakers = all_speakers.keys()

# visualize vectors
if st.session_state.visualize_vectors:
    vector_visualization = plot_speakers(st.session_state.sentence_model,
                                         all_speakers)
    st.pyplot(vector_visualization)

# visualize topics
if st.session_state.visualize_topics:
    st.write("File topics")
    topics = st.session_state.db.get_topics_by_speaker()
    # get topic name, count, and speaker name
    data = [[topic[1], topic[3], topic[5]] for topic in topics
            if topic[5] in all_speakers]
    df = pd.DataFrame(data, columns=["Topic", "Count", "Speaker"])
    st.dataframe(df)
