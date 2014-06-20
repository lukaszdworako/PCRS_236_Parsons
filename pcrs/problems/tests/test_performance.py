class TestSubmissionHistoryDatabaseHits:
    """
    Test the number of database hits when loading the submission history.

    Should be kept constant.
    """
    db_hits = 10

    def test_num_hits(self):
        self.client.login(username=self.student.username)
        with self.assertNumQueries(self.db_hits):
            response = self.client.post(self.url)
