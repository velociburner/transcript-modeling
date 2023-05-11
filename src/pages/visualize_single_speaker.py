import streamlit as st
from visualize import plot_speakers

st.set_page_config(page_title="Visualization")

speaker_name = st.session_state.selected
speaker_development = {}
for i, section in enumerate(st.session_state.sections):
    speaker_development[speaker_name + str(i)] = section[speaker_name]

if st.session_state.visualize_vectors:
    vector_visualization = plot_speakers(st.session_state.sentence_model, speaker_development)
if st.session_state.visualize_topics:
    pass
    # TODO list characteristic topics
