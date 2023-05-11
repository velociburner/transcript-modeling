import unittest
import sqlite3

from src.database import TopicDatabase


class DatabaseTest(unittest.TestCase):
    """Tests the functionality of the TopicsDatabase."""

    def setUp(self):
        conn = sqlite3.connect(":memory:")
        self.db = TopicDatabase(conn)

    def testFiles(self):
        self.db.add_file("filename", ["foo", "bar"])
        files = self.db.get_files()
        assert len(files) == 1

        self.db.add_file("filename", ["foo", "bar"])
        files = self.db.get_files()
        assert len(files) == 1

        self.db.add_file("othername", ["foo", "bar"])
        files = self.db.get_files()
        assert len(files) == 2

    def testSpeakers(self):
        self.db.update_speaker("Joe", ["foo", "bar"])
        speakers = self.db.get_speakers()
        assert len(speakers) == 1

        joe = speakers[0]
        num_sentences = joe[-1]
        assert num_sentences == 2

        self.db.update_speaker("Joe", ["foo", "bar"])
        speakers = self.db.get_speakers()
        assert len(speakers) == 1
        joe = speakers[0]
        num_sentences = joe[-1]
        assert num_sentences == 4

        self.db.update_speaker("Bob", ["foo", "bar"])
        speakers = self.db.get_speakers()
        assert len(speakers) == 2

    def testTopics(self):
        self.db.update_speaker("Joe", ["foo", "bar"])

        self.db.add_topic(42, "topic_name", "Joe")
        self.db.add_topic(42, "topic_name", "Joe")
        topics = self.db.get_topics()
        assert len(topics) == 1

        joe = topics[0]
        count = joe[-1]
        assert count == 2

        self.db.add_topic(100, "topic_name", "Joe")
        topics = self.db.get_topics()
        assert len(topics) == 2

        self.db.update_speaker("Bob", ["foo", "bar"])
        self.db.add_topic(100, "topic_name", "Bob")
        topics = self.db.get_topics()
        assert len(topics) == 3


if __name__ == "__main__":
    unittest.main()
