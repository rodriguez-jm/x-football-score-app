import unittest
import os
import logging
from unittest.mock import patch
from main import *

class TestMain(unittest.TestCase):

    def setUp(self):
        self.fixture = {
            'fixture': {
                'id': 123,
                'date': '2023-01-01T12:00:00+00:00',
                'status': {'long': 'Match Finished'}
            },
            'teams': {
                'home': {'name': 'Home Team'},
                'away': {'name': 'Away Team'}
            },
            'goals': {'home': 2, 'away': 1}
        }

    def tearDown(self):
        if os.path.exists(completed_file):
            os.remove(completed_file)
        if os.path.exists(fixture_ids_file):
            os.remove(fixture_ids_file)
        if os.path.exists(all_fixture_ids_file):
            os.remove(all_fixture_ids_file)

    def test_get_fixtures_by_date_success(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'response': [self.fixture]}
            fixtures = get_fixtures_by_date(url, '2023-01-01')
            self.assertEqual(len(fixtures), 1)
            self.assertEqual(fixtures[0], self.fixture)

    def test_get_fixtures_by_date_failure(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 500
            with self.assertRaises(SystemExit) as cm:
                get_fixtures_by_date(url, '2023-01-01')
            self.assertEqual(cm.exception.code, 1)

    def test_store_fixture_ids(self):
        fixtures = [self.fixture]
        store_fixture_ids(fixtures, all_fixture_ids_file)
        self.assertTrue(os.path.exists(all_fixture_ids_file))
        with open(all_fixture_ids_file, 'r') as file:
            fixture_ids = file.readlines()
            self.assertEqual(len(fixture_ids), 1)
            self.assertEqual(int(fixture_ids[0]), self.fixture['fixture']['id'])

    def test_print_fixture_status(self):
        with patch('main.send_tweet') as mock_send_tweet:
            print_fixture_status(self.fixture)
            mock_send_tweet.assert_called_once_with(
                "FULL TIME: Home Team 2 - 1 Away Team")

    def test_is_fixture_id_sent(self):
        with open(fixture_ids_file, 'w') as file:
            file.write(str(self.fixture['fixture']['id']) + '\n')
        self.assertTrue(is_fixture_id_sent(self.fixture['fixture']['id'], fixture_ids_file))
        self.assertFalse(is_fixture_id_sent(456, fixture_ids_file))

    def test_mark_fixture_id_as_sent(self):
        mark_fixture_id_as_sent(self.fixture['fixture']['id'])
        with open(fixture_ids_file, 'r') as file:
            fixture_ids = file.readlines()
            self.assertEqual(len(fixture_ids), 1)
            self.assertEqual(int(fixture_ids[0]), self.fixture['fixture']['id'])

    def test_compare_fixture_files_equal(self):
        with open(all_fixture_ids_file, 'w') as f1, open(fixture_ids_file, 'w') as f2:
            f1.write(str(self.fixture['fixture']['id']) + '\n')
            f2.write(str(self.fixture['fixture']['id']) + '\n')
        self.assertTrue(compare_fixture_files(all_fixture_ids_file, fixture_ids_file))

    def test_compare_fixture_files_not_equal(self):
        with open(all_fixture_ids_file, 'w') as f1, open(fixture_ids_file, 'w') as f2:
            f1.write(str(self.fixture['fixture']['id']) + '\n')
            f2.write(str(self.fixture['fixture']['id'] + 1) + '\n')
        self.assertFalse(compare_fixture_files(all_fixture_ids_file, fixture_ids_file))

    def test_send_tweet_success(self):
        with patch('tweepy.Client.create_tweet') as mock_create_tweet:
            send_tweet("Test tweet")
            mock_create_tweet.assert_called_once_with(text="Test tweet", user_auth=True)

    def test_send_tweet_failure(self):
        with patch('tweepy.Client.create_tweet') as mock_create_tweet:
            mock_create_tweet.side_effect = tweepy.errors.TweepyException("Error sending tweet")
            with self.assertRaises(SystemExit) as cm:
                send_tweet("Test tweet")
            self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()