import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA


def plot_speakers(model, speakers: dict[str, list]):
    # Run through model and generate vectors
    vector_list = []
    for speaker in speakers:
        sentences = speakers[speaker]
        vector = model.encode(sentences).mean(axis=0)
        vector_list.append(vector)

    vectors = np.array(vector_list)
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)

    # Separate the coordinates into x, y, and z arrays
    x = coords[:, 0]
    y = coords[:, 1]
    z = coords[:, 2]

    # Create a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z)

    # Annotate plot with speaker names
    for i, speaker in enumerate(speakers):
        ax.text(x[i], y[i], z[i], speaker, fontsize=8)

    plt.show()
