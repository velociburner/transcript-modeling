class TopicDatabase:
    """Stores a database connection and the associated functionality for files,
    speakers, and topics."""

    def __init__(self, conn):
        self.conn = conn
        self.create_tables()

    def create_tables(self):
        """Creates tables in the database if they don't already exist."""

        files = """CREATE TABLE IF NOT EXISTS Files (
                        FileID INTEGER PRIMARY KEY,
                        FileName VARCHAR(255),
                        SourceName VARCHAR(255),
                        NumTokens INTEGER,
                        NumLines INTEGER
                    );"""
        speakers = """CREATE TABLE IF NOT EXISTS Speakers (
                        SpeakerID INTEGER PRIMARY KEY,
                        SpeakerName VARCHAR(255) UNIQUE,
                        NumSentences INTEGER
                    );"""
        topics = """CREATE TABLE IF NOT EXISTS Topics (
                        TopicID INTEGER,
                        TopicName VARCHAR(255),
                        SpeakerID INTEGER,
                        Count INTEGER,
                        FOREIGN KEY (SpeakerID) REFERENCES Speakers(SpeakerID)
                    );"""
        self.conn.execute(files)
        self.conn.execute(speakers)
        self.conn.execute(topics)
        self.conn.commit()

    def _get_source(self, filename: str):
        """Returns the source of where the file comes from based on the
        name."""

        if filename.startswith("CNN"):
            return "CNN"
        if filename.startswith("PBS") or filename.startswith("cpb"):
            return "PBS"
        if filename.startswith("NPR"):
            return "NPR"
        if filename[0].isdigit() and filename[1].isdigit():
            if filename[2].isdigit():
                return "tma"
            else:
                return "ars_paradoxica"

        return "Project Gutenberg"

    def add_file(self, name: str, lines: list[str]):
        """Adds a file to the database, if it doesn't already exist yet."""

        result = self.conn.execute(
            "SELECT * FROM Files WHERE Filename=?;", (name, )
        )
        file = result.fetchone()
        if file is not None:
            return

        num_tokens = num_lines = 0
        for line in lines:
            num_tokens += len(line.split())
            num_lines += 1
        source = self._get_source(name)

        sql = """INSERT INTO
                    Files (FileName, SourceName, NumTokens, NumLines)
                    VALUES (?, ?, ?, ?);"""
        self.conn.execute(sql, (name, source, num_tokens, num_lines))

        self.conn.commit()

    def update_speaker(self, name: str, sentences: list[str]):
        """Increases the number of sentences of a given speaker if it is
        already in the table, or creates a new entry if not."""

        result = self.conn.execute(
            "SELECT * FROM Speakers WHERE SpeakerName=?;", (name, )
        )
        speaker = result.fetchone()
        if speaker is not None:
            id, speaker_name, num_sentences = speaker
            sql = "UPDATE Speakers SET NumSentences=?+? WHERE SpeakerID=?;"
            self.conn.execute(sql, (num_sentences, len(sentences), id))
        else:
            sql = """INSERT INTO Speakers (SpeakerName, NumSentences)
                        VALUES (?, ?);"""
            self.conn.execute(sql, (name, len(sentences)))

        self.conn.commit()

    def add_topic(self, topic_id: int, topic_name: str, speaker_name: str):
        sql = "SELECT SpeakerID FROM Speakers WHERE SpeakerName=?;"
        speaker = self.conn.execute(sql, (speaker_name, ))
        speaker_id = speaker.fetchone()[0]

        sql = "SELECT * FROM Topics WHERE TopicID=? AND SpeakerID=?;"
        result = self.conn.execute(sql, (topic_id, speaker_id))
        topic = result.fetchone()

        if topic is not None:
            count = topic[-1]
            sql = """UPDATE Topics SET Count=?+1
                        WHERE TopicID=? AND SpeakerID=?;"""
            self.conn.execute(sql, (count, topic_id, speaker_id))
        else:
            sql = """INSERT INTO
                            Topics (TopicID, TopicName, SpeakerID, Count)
                            VALUES (?, ?, ?, ?);"""
            self.conn.execute(sql, (topic_id, topic_name, speaker_id, 1))

        self.conn.commit()

    def _get(self, table):
        """Returns the rows of the given table."""
        # can't use parameter substitution for table names
        result = self.conn.execute(f"SELECT * FROM {table};")
        return result.fetchall()

    def get_files(self):
        """Returns the rows of the Files table."""
        return self._get("Files")

    def get_speakers(self):
        """Returns the rows of the Speakers table."""
        return self._get("Speakers")

    def get_topics(self):
        """Returns the rows of the Topics table."""
        return self._get("Topics")

    def get_topics_by_speaker(self):
        """Returns the joined table of topics and speakers."""
        sql = """SELECT * FROM Topics JOIN Speakers ON
                Topics.SpeakerID=Speakers.SpeakerID"""
        return self.conn.execute(sql)

    def close(self):
        """Closes the connection to the database."""
        self.conn.close()
