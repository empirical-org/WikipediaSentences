"""Tests sva_classifier. Sparse set of tests."""
import unittest
from porcupine import check

class TestClassifierMethods(unittest.TestCase):

    def test_check_sva_feedback(self):
        feedback = check("The girl run incredibly fast.")
        self.assertEqual(feedback.primary_error, 'SUBJECT_VERB_AGREEMENT_ERROR')

    def test_check_spelling_feedback(self):
        feedback = check("The scientest made a spelling mistake.")
        self.assertEqual(feedback.primary_error, 'SPELLING_ERROR')

    def test_check_other_language_tool_feedback(self):
        feedback = check("He would love to swims today.")
        self.assertEqual(feedback.primary_error, 'OTHER_ERROR')

    def test_check_strong_sentence_feedback(self):
        feedback = check("This is a strong sentence.")
        self.assertEqual(feedback.primary_error, None)

if __name__ == '__main__':
    unittest.main()
