from sklearn.feature_extraction.text import CountVectorizer


# based on the "fine tune" section of our modeling notebook
def get_intertopic_distance_map(text, model):
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=n(1, 3))
    model.update_topics(text, vectorizer_model=vectorizer_model)
    return model.visualize_topics()