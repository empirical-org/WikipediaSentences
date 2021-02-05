from quillnlp.preprocessing.checks import ProfanityCheck, MultipleSentencesCheck


def test_profanity_check():

    sentences = [("You shall not pass", 0),
                 ("Kiss my ass", 1),
                 ("Kiss my ass, idiot", 1),
                 ("Ass", 1),
                 ("She gave me a blow job", 1)]

    check = ProfanityCheck()
    for sentence, number in sentences:
        feedback = check.check_from_text(sentence, "")
        print(sentence, feedback)
        assert len(feedback) == number


def test_multiple_sentences_check():

    sentences = [("He loves me. He loves me not.", 1),
                 ("He loves me.", 0),
                 ("He loves me not.", 0)]

    check = MultipleSentencesCheck()
    for sentence, number in sentences:
        feedback = check.check_from_text(sentence, "")
        print(sentence, feedback)
        assert len(feedback) == number
