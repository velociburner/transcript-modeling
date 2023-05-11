`home.py`

This is the home page for our Streamlit app. The database is initialized, models are loaded, and the user uploads a file. The user decides whether to sectionize the document, visualize vector representations, and/or visualize topics. These preferences are saved into Streamlit’s session state. The file is preprocessed, and then processed as specified. From here, the user can view results by clicking “visualize whole script” on the left sidebar.

`consolidate_lines.py`

This file contains code to clean scripts by removing problematic characters, marking stage directions, and normalizing formatting. See the comments on individual functions for more detail.

`database.py`

This file contains the functionality for storing and retrieving entries from a SQlite database. It contains one class TopicDatabase, which stores a database connection upon initialization. The connection must be obtained prior to creating an instance of this class.

Example:
```py
db_file = “database.db”
conn = sqlite3.connect(db_file)
db = TopicDatabase(conn)
```

`get_transcripts.py`

This code was used to extract transcripts from XML files. These transcripts were further preprocessed by going through consolidate_lines.py.

`process_scripts.py`

This file is used for handling transcripts when they are uploaded to the web app. It can preprocess the lines using
functions from `consolidate_lines.py` and then split the dialogue into different speakers.

`sectionize.py`

This code sectionizes a script into acts, scenes, dialogue, stage direction, and extraneous metadata. Later, we use this by only processing the text located within acts.

`visualize.py`

This file contains a single function plot_speakers(). This function takes an embedding model and a mapping from speakers to sentences, and generates a 3d plot of the average embeddings of each speaker.
