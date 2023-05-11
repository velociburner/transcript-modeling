# visualize vector representations and topics for all speakers in a script
# users can select a speaker to see that speaker's individual visualization (visualize_singlespeaker.py)
import streamlit as st
from visualize import plot_speakers
from visualize_topics import get_intertopic_distance_map
# from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Visualization")

all_speakers = set()
# for section, 
for section in st.session_state.sections:
    all_speakers.update(section.keys())  # get all speaker names from this section
    # visualize vectors
    if st.session_state.visualize_vectors:
        vector_visualization = plot_speakers(st.session_state.sentence_model, section)
    # plot_speakers(topic_model, speakers)
    # visualize topic model
    if st.session_state.visualize_topics:
        pass
        # TODO put table of topics

# checkboxes for speaker names
st.session_state.selected = st.radio("Choose a character to view in more detail:", tuple(all_speakers))