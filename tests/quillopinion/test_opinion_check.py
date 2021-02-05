import re
import pytest

from quillopinion.opinioncheck import OpinionCheck


@pytest.fixture
def validate():

    def check(sentence, prompt, is_opinion):
        checker = OpinionCheck()
        feedback = checker.check_from_text(sentence, prompt)

        assert (len(feedback) >= 1) == is_opinion
    return check


def test_opinioncheck1():
    sentence = "We need to eat less meat so climate change can hopefully be reduced."
    prompt = "We need to eat less meat so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Common Opinionated Phrases Keyword Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 56


def test_opinioncheck2():
    sentence = "We need to end climate change so I'm thinking of eating less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 2
    assert feedback[0].type == "First-Person Opinionated Phrase Keyword Check"
    assert feedback[0].start == 33
    assert feedback[0].end == 45


def test_opinioncheck3():
    sentence = "We need to end climate change so you have to eat less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Second-Person Reference Keyword Check"
    assert feedback[0].start == 33
    assert feedback[0].end == 36


def test_opinioncheck4():
    sentence = "We need to end climate change so it would perhaps be better if people ate less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Using Perhaps"
    assert feedback[0].start == 42
    assert feedback[0].end == 49


def test_opinioncheck5():
    sentence = "We need to end climate change so all Americans should eat vegetables."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Using Should"
    assert feedback[0].start == 47
    assert feedback[0].end == 53


def test_opinioncheck6(validate):
    sentence = "We need to end climate change because Barack Obama says all Americans should eat vegetables."
    prompt = "We need to end climate change because"

    validate(sentence, prompt, False)


def test_opinioncheck7():
    sentence = "We need to end climate change so all Americans ought to eat vegetables."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Using Ought"
    assert feedback[0].start == 47
    assert feedback[0].end == 52


def test_opinioncheck8(validate):
    sentence = "We need to end climate change because Barack Obama says all Americans ought to eat vegetables."
    prompt = "We need to end climate change because"

    validate(sentence, prompt, False)


def test_opinioncheck9(validate):
    sentence = "Plastic bag reduction laws are helpful, so according to this article, plastic bag usage should be limited."
    prompt = "Plastic bag reduction laws are helpful, so"

    validate(sentence, prompt, False)


def test_opinioncheck10(validate):
    sentence = "Plastic bag reduction laws are helpful, but not enough of " \
               "the general public is aware of the consumption and amount " \
               "of plastics consumed daily per household in the US."
    prompt = "Plastic bag reduction laws are helpful, but"

    validate(sentence, prompt, False)


def test_opinioncheck11(validate):
    sentence = "Plastic bag reduction laws are helpful, because by those " \
               "laws we learn to protect environment , because plastic bag " \
               "reduction is very harmful for environment and people's health."
    prompt = "Plastic bag reduction laws are helpful, because"

    validate(sentence, prompt, True)


def test_opinioncheck12(validate):
    sentence = "Plastic bag reduction laws are helpful, because not only " \
               "will it be good for our environment, but equally as good " \
               "for people health who frequently use plastic bags."
    prompt = "Plastic bag reduction laws are helpful, because"

    validate(sentence, prompt, True)


def test_opinioncheck13(validate):
    sentence = "Methane from cow burps harms the environment, so it needs to be addressed soon."
    prompt = "Methane from cow burps harms the environment, so"

    validate(sentence, prompt, True)


def test_opinioncheck14(validate):
    sentence = "Methane from cow burps harms the environment, so it's not wise to eat meat."
    prompt = "Methane from cow burps harms the environment, so"

    validate(sentence, prompt, True)


def test_opinioncheck15(validate):
    sentence = "Plastic bag reduction laws are helpful, but the " \
               "downside is that when we reduce the creation of plastic " \
               "bags, some people will lose their jobs."
    prompt = "Plastic bag reduction laws are helpful, but"

    validate(sentence, prompt, True)


def test_opinioncheck16(validate):
    sentence = "Plastic bag reduction laws are helpful, but " \
               "lets not exaggerate."
    prompt = "Plastic bag reduction laws are helpful, but"

    validate(sentence, prompt, True)


def test_opinioncheck17(validate):
    sentence = "Large amounts of meat consumption are harming the environment, " \
               "so continue to eat cows more so that way they die faster."
    prompt = "Large amounts of meat consumption are harming the environment, so"

    validate(sentence, prompt, True)


def test_opinioncheck18():
    sentence = "It's critical that we change this."
    prompt = ""

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) > 0
    assert feedback[0].match == "It's critical"
    assert feedback[0].start == 0


def test_opinioncheck19():
    sentence = "It isn't a good idea."
    prompt = ""

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) > 0
    assert feedback[0].match == "isn't a good idea"
    assert feedback[0].start == 3


def test_initial_verb():

    sentences = [("Large amounts of meat consumption are harming the environment, "
                  "so there is no problem in this sentence.",
                  "Large amounts of meat consumption are harming the environment, so", "", 0, None),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so see there is a problem.",
                  "Large amounts of meat consumption are harming the environment, so", "see", 66,
                  "Starts with Verb Check"),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so listening will not help.",
                  "Large amounts of meat consumption are harming the environment, so", "", 0, None),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so stopping to eat meat would be a good idea.",
                  "Large amounts of meat consumption are harming the environment, so", "", 0, None),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so ground meat is a problem, too.",
                  "Large amounts of meat consumption are harming the environment, so", "", 0, None),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so learned behavior will do the trick.",
                  "Large amounts of meat consumption are harming the environment, so", "", 0, None)
                 ]

    check = OpinionCheck()
    for sentence, prompt, word, index, opinion_type in sentences:
        feedback = check.check_from_text(sentence, prompt)
        print(feedback)

        if opinion_type is not None:
            assert len(feedback) > 0
            assert feedback[0].match == word
            assert feedback[0].start == index
            assert feedback[0].type == opinion_type
        else:
            assert len(feedback) == 0


def test_opinioncheck_order():
    sentence = "Large amounts of meat consumption are harming the environment, " \
               "so you and I should eat less meat."

    prompt = "Large amounts of meat consumption are harming the environment, so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    print(feedback)

    assert len(feedback) == 3
    assert feedback[0].type == "Using Should"
    assert feedback[1].type == "First-Person Reference Keyword Check"
    assert feedback[2].type == "Second-Person Reference Keyword Check"
