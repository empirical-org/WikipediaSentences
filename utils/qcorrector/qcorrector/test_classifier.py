"""Tests sva_classifier. Sparse set of tests."""
import unittest
from check import check, Feedback

class TestClassifierMethods(unittest.TestCase):

    def test_check_sva_feedback(self):
        sent = "The girl run incredibly fast."
        actual_fb = check(sent)
        self.assertEqual(actual_fb.primary_error, 'SUBJECT_VERB_AGREEMENT_ERROR')

    def test_check_spelling_feedback(self):
        sent = "The scientest made a spelling mistake."
        actual_fb = check(sent)
        self.assertEqual(actual_fb.primary_error, 'SPELLING_ERROR')

if __name__ == '__main__':
    unittest.main()
