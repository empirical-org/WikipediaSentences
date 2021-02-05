from quillnlp.grammar.verbs import agreement, perfect, passive, tense
from quillnlp.grammar.verbutils import replace_past_simple_with_past_perfect


def test_passive_without_be():

    input = "The lion is known for its ferocious roar."
    output = "The lion known for its ferocious roar."

    sentence = passive.PassiveWithoutBeErrorGenerator().generate_from_text(input)
    assert output == sentence[0]


def test_passive_with_incorrect_be_form():

    input = "The lion is known for its ferocious roar."
    output1 = "The lion are known for its ferocious roar."
    output2 = "The lion been known for its ferocious roar."
    output3 = "The lion be known for its ferocious roar."
    output4 = "The lion am known for its ferocious roar."

    sentence = passive.PassiveWithIncorrectBeErrorGenerator().generate_from_text(input)
    assert sentence[0] in set([output1, output2, output3, output4])


def test_replace_past_participle_by_simple_past():

    input = "I had forgotten to pay the bill."
    output = "I had forgot to pay the bill."

    sentence = perfect.PerfectTenseWithSimplePastErrorGenerator().generate_from_text(input)
    assert output == sentence[0]


def test_remove_have_from_perfect():

    input_output_pairs = [("The dog has eaten my homework.",
                           "The dog eaten my homework."),
                          ("I've never been there.",
                           "I never been there."),
                          ("She hasn't broken the world record.",
                           "She not broken the world record."),
                          ("I have been here.",
                           "I been here."),
                          ("I have been working here for a long time.",  # Do not change perfect progressive
                           "I have been working here for a long time."),
                          ("The lion has been known for its ferocious roar.", # Do not change passive perfect
                           "The lion has been known for its ferocious roar.")]

    for input, output in input_output_pairs:
        sentence = perfect.PerfectTenseWithoutHaveErrorGenerator().generate_from_text(input)
        assert output == sentence[0]


def test_remove_have_from_perfect_progressive():

    input_output_pairs = [("I have been here.",
                           "I have been here."),
                          ("I have been working here for a long time.",
                           "I been working here for a long time."),
                          ("I've been working here for a long time.",
                           "I been working here for a long time."),
                          ("I haven't been working here for a long time.",
                           "I not been working here for a long time.")]

    for input, output in input_output_pairs:
        sentence = perfect.PerfectProgressiveWithoutHaveErrorGenerator().generate_from_text(input)
        assert output == sentence[0]


def test_remove_have_from_passive_perfect():

    input_output_pairs = [("The dog has eaten my homework.",
                           "The dog has eaten my homework."),
                          ("I've never been there.",
                           "I've never been there."),
                          ("She hasn't broken the world record.",
                           "She hasn't broken the world record."),
                          ("I have been here.",
                           "I have been here."),
                          ("I have been working here for a long time.",  # Do not change perfect progressive
                           "I have been working here for a long time."),
                          ("The lion has been known for its ferocious roar.",
                           "The lion been known for its ferocious roar."),
                          ("The lion hasn't been known for its ferocious roar.",
                           "The lion not been known for its ferocious roar.")]

    for input, output in input_output_pairs:
        sentence = perfect.PassivePerfectWithoutHaveErrorGenerator().generate_from_text(input)
        assert output == sentence[0]


def test_past_perfect_with_incorrect_participle():

    input_output_pairs = [("Their stories have been forgotten.",
                           "Their stories have been forgot.")]

    for input, output in input_output_pairs:
        sentence = perfect.PassivePerfectWithIncorrectParticipleErrorGenerator().generate_from_text(input)
        assert output == sentence[0]


def test_incorrect_past_perfect():

    input = "I had already eaten dinner when you called."
    output = "I had already eaten dinner when you had called."

    sentence = replace_past_simple_with_past_perfect(input)

    assert output == sentence


def test_incorrect_past_passive():

    input = "My dinner was eaten a long time ago."
    output = "My dinner was ate a long time ago."

    sentence = passive.PassivePastTenseAsParticipleErrorGenerator().generate_from_text(input)

    assert output == sentence[0]


def test_incorrect_third_person_verb():

    input = "The wind blows through the leaves."
    output = "The wind blow through the leaves."

    sentence = agreement.SubjectVerbAgreementWithSimpleNounErrorGenerator().generate_from_text(input)

    assert output == sentence[0]


def test_incorrect_verb_after_personal_pronoun():

    # TODO: this is more specific than the previous rule.
    # Make sure this is run first.

    input_output_pairs = [("He lives in Belgium.", "He live in Belgium.")]

    for input, output in input_output_pairs:
        sentence = agreement.SubjectVerbAgreementWithPronounErrorGenerator().generate_from_text(input)

        assert output == sentence[0]


def test_plural_after_collective():

    # TODO: again a more specific rule

    input = "The herd is stampeding"
    output = "The herd are stampeding"

    error_generator = agreement.SubjectVerbAgreementWithCollectiveNoun()
    sentence = error_generator.generate_from_text(input)
    assert sentence[0] == output
    assert sentence[1] == [(9, 12, error_generator.name)]


def test_plural_after_indefinite():

    # TODO: is more specific

    input = "Each student is expected to present"
    output = "Each student are expected to present"

    error_generator = agreement.SubjectVerbAgreementWithIndefinitePronoun()
    sentence = error_generator.generate_from_text(input)

    assert sentence[0] == output
    assert sentence[1] == [(13, 16, error_generator.name)]


def test_incorrect_verb_after_neither_nor():

    input = "Neither the receptionist nor the lawyers remembers what happened that night."
    output = "Neither the receptionist nor the lawyers remember what happened that night."

    sentence = agreement.SubjectVerbAgreementWithNeitherNorErrorGenerator().generate_from_text(input)
    assert sentence[0] == output


def test_incorrect_verb_after_neither_nor2():

    input = "Neither the players nor the coach is awarded the trophy."
    output = "Neither the players nor the coach are awarded the trophy."

    sentence = agreement.SubjectVerbAgreementWithNeitherNorErrorGenerator().generate_from_text(input)
    assert sentence[0] == output


def test_incorrect_verb_after_either_or():

    input = "Either the players or the coach are awarded the trophy."
    output = "Either the players or the coach is awarded the trophy."

    sentence = agreement.SubjectVerbAgreementWithEitherOrErrorGenerator().generate_from_text(input)
    assert sentence[0] == output


def test_incorrect_present_progressive():

    input = "I have been working here for a long time."
    output = "I be working here for a long time."

    sentence = perfect.PerfectProgressiveWithIncorrectBeAndWithoutHaveErrorGenerator().generate_from_text(input)

    assert sentence[0] == output
    assert sentence[1] == [[2, 4, perfect.PerfectProgressiveWithIncorrectBeAndWithoutHaveErrorGenerator().name]]


def test_simple_past_instead_of_past_perfect():

    input = "He had seen her before."
    output = "He saw her before."

    sentence = tense.SimplePastInsteadOfPastPerfectErrorGenerator().generate_from_text(input)

    assert sentence[0] == output


def test_simple_past_instead_of_present_perfect():

    input = "I have never eaten cake before."
    output = "I never ate cake before."

    sentence = tense.SimplePastInsteadOfPresentPerfectErrorGenerator().generate_from_text(input)

    assert sentence[0] == output


def test_past_perfect_instead_of_simple_past():

    input = "When I heard you screaming, it scared me."
    output = "When I heard you screaming, it had scared me."

