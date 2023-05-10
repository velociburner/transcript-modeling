# What you did and why:
We created a web application that allows users to upload transcript files, which are then processed and visualized, depending on the options selected. We pretrained a topic model using a bunch of transcripts, and then used that to process the new files. We chose this project because topic modeling is an interesting area of information extraction. It is also not totally straightforward how to do topic modeling of dialogue, since there was a lot of preprocessing involved.
# How you implemented it, broadly:
First, we obtained scripts and transcripts from a variety of sources, as described in the section “What went right and what went wrong” below. We devised rules to re-format them into a more easily parsable format, and created a sectionizer to extract only the relevant parts of a document.

We used the BERTopic python package for implementing topic modeling. It allows for tuning of every component of the pipeline (embeddings, clustering, etc.). For the word embeddings, we experimented with different SBERT models using SentenceTransformers, as well as spaCy’s non-transformer models. Each line of the transcripts was treated as a single document, and then we obtained a sentence embedding that was used to generate the topics. The best model from tuning was “all-MiniLM-L12-v2”. We saved the results from training this model on the training documents and used that for the web app.

We integrated the above into a Streamlit app, where a user can upload a file that is processed as described. There is also an SQLite database integrated into this application.
We used the sqlite3 package for interfacing with a SQlite database. The database consists of three tables: Files, Speakers, and Topics. These store information about the files and speakers each time a file is uploaded. They store which files have been uploaded, which speakers had dialogue in each file, and the topics associated with each speaker’s dialogue across all documents.

# What went right and what went wrong:
## Right:
* Data procurement: We were able to obtain 55 plays and multi-play collections from Project Gutenberg. In combination with news transcripts and podcast transcripts, these provided a sufficiently large and varied data source to create rules that could be applied to scripts and transcripts in general.
* Sectionizing: After implementing and testing the preprocessing functions, we had enough of a sense for the formatting of these documents that creating a sectionizer was easier than anticipated.
* Topic model: The best model from training had a silhouette score of 0.752, which is pretty decent. We were able to use this to classify new documents into topics that weren’t too similar to each other.
## Wrong:
* Data access: It was surprisingly difficult to access large amounts of news transcripts. We already had a few on hand from another project, but our intended source for more PBS and NPR transcripts was not able to provide us with any more. We were eventually able to obtain a larger set, but not until this project was well underway.
* Formatting: Playwrights are more creative with their formatting than anticipated. The greatest difficulties were found when documents included lines in more than one format. For instance:

		HENRY.
	                      	The lack of love!

		ROSAMUND.
		Of one we love. Nay, I would not be bold,
		Yet hoped ere this you might--
	    	                	[_Looks earnestly at him_.
* However, the amount of variation between and within documents was manageable. It could mostly be accounted for by detecting the basic formatting rules of an individual file before it is preprocessed.
* Topic modeling issues: Some bert models and spacy transformer models were really hard to work with. The format wasn’t compatible with BERTopic, so we just tried more SBERT models instead. Besides, they were faster and generally worked better for this task.
* Model: It took a while to figure out how to save the best model in a place that could be easily downloaded when building the Docker image. We tried uploading it to a Brandeis server and a number of free file hosting websites, which were all either too slow or didn’t work. In the end, we had to create a free Amazon web service for object storage and upload it there. Even that was a multistep process though.
# Who implemented what
Spencer implemented the data procurement, sectionizing, preprocessing and rules, and the Streamlit app.

Josh implemented the topic modeling and experiments, the visualizations in the Streamlit app, the database functionality, and saving, storing, and downloading the model into the Docker image.