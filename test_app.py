import unittest
from app import app, load_hebrew_words

class TestCrosswordSolver(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_word_list_loaded(self):
        # Verify that the word list is loaded and contains known words
        words = load_hebrew_words()
        self.assertIsInstance(words, list)
        self.assertIn('מחשב', words)
        self.assertIn('שלום', words)
        self.assertGreater(len(words), 0)

    def test_find_machshev(self):
        # Looking for a 4-letter word ending with 'ב' (should match מחשב)
        pattern = '   ב'
        response = self.client.post('/find_words', json={
            'pattern': pattern,
            'length': 4
        })
        data = response.get_json()
        self.assertIn('מחשב', data['words'])

    def test_find_shalom(self):
        # Looking for a 4-letter word starting with 'ש' (should match שלום)
        pattern = 'ש   '
        response = self.client.post('/find_words', json={
            'pattern': pattern,
            'length': 4
        })
        data = response.get_json()
        self.assertIn('שלום', data['words'])

    def test_no_match(self):
        # Looking for a 4-letter word with impossible pattern
        pattern = 'קקקק'
        response = self.client.post('/find_words', json={
            'pattern': pattern,
            'length': 4
        })
        data = response.get_json()
        self.assertEqual(data['words'], [])

    def test_find_7_letter(self):
        # Looking for a 7-letter word starting with 'א' (should match אינטרנט, אוטובוס)
        pattern = 'א      '
        response = self.client.post('/find_words', json={
            'pattern': pattern,
            'length': 7
        })
        data = response.get_json()
        self.assertIn('אינטרנט', data['words'])
        self.assertIn('אוטובוס', data['words'])

if __name__ == '__main__':
    unittest.main() 