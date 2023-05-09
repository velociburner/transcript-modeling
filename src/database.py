def create_tables(db):
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
                    TopicID INTEGER PRIMARY KEY,
                    Topic VARCHAR(255),
                    SpeakerID INTEGER,
                    FOREIGN KEY (SpeakerID) REFERENCES Speakers(SpeakerID)
                );"""
    db.execute(files)
    db.execute(speakers)
    db.execute(topics)
    db.commit()


def get_source(filename):
    """Returns the source of where the file comes from based on the name."""

    if filename.startswith("CNN"):
        return "CNN"
    if filename.startswith("PBS") or filename.startswith("cpb"):
        return "PBS"
    if filename[0].isdigit() and filename[1].isdigit():
        if filename[2].isdigit():
            return "tma"
        else:
            return "ars_paradoxica"

    return "Project Gutenberg"


def add_file(db, name, lines):
    """Adds a file to the database, if it doesn't already exist yet."""

    result = db.execute("SELECT * FROM Files WHERE Filename=?;", (name,))
    file = result.fetchone()
    if file is not None:
        return

    num_tokens = num_lines = 0
    for line in lines:
        num_tokens += len(line.split())
        num_lines += 1
    source = get_source(name)

    sql = """INSERT INTO
                Files (FileName, SourceName, NumTokens, NumLines)
                VALUES (?, ?, ?, ?);"""
    db.execute(sql, (name, source, num_tokens, num_lines))


def update_speaker(db, name, sentences):
    """Increases the number of sentences of a given speaker if it is already in
    the table, or creates a new entry if not."""

    result = db.execute("SELECT * FROM Speakers WHERE SpeakerName=?;", (name,))
    speaker = result.fetchone()
    if speaker is not None:
        id, speaker_name, num_sentences = speaker
        sql = "UPDATE Speakers SET NumSentences=?+? WHERE SpeakerID=?;"
        db.execute(sql, (num_sentences, len(sentences), id))
    else:
        sql = "INSERT INTO Speakers (SpeakerName, NumSentences) VALUES (?, ?);"
        db.execute(sql, (name, len(sentences)))

    db.commit()
