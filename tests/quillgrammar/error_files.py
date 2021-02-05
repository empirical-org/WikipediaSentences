from quillgrammar.grammar.constants import GrammarError


files = [
    {
        "error": GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value,
        "positive": "data/validated/grammar_errors/incorrect-irregular-past-tense-positive.txt",
        "negative": "data/validated/grammar_errors/incorrect-irregular-past-tense-negative.txt"
    },
#    {
#        "error": GrammarError.SVA_COLLECTIVE_NOUN.value,
#        "positive": "data/validated/grammar_errors/subject-verb-agreement-with-collective-noun-positive.txt",
#        "negative": "data/validated/grammar_errors/subject-verb-agreement-with-collective-noun-negative.txt"
#    },
    {
        "error": GrammarError.MAN_MEN.value,
        "positive": "data/validated/grammar_errors/man-men-positive.txt",
        "negative": "data/validated/grammar_errors/man-men-negative.txt"
    },
    {
        "error": GrammarError.WOMAN_WOMEN.value,
        "positive": "data/validated/grammar_errors/woman-women-positive.txt",
        "negative": "data/validated/grammar_errors/woman-women-negative.txt"
    },
    {
        "error": GrammarError.CAPITALIZATION.value,
        "positive": "data/validated/grammar_errors/capitalization-positive.txt",
        "negative": "data/validated/grammar_errors/capitalization-negative.txt"
    },
    {
        "error": GrammarError.REPEATED_WORD.value,
        "positive": "data/validated/grammar_errors/repeated-word-positive.txt",
        "negative": "data/validated/grammar_errors/repeated-word-negative.txt"
    },
    {
        "error": GrammarError.QUESTION_MARK.value,
        "positive": "data/validated/grammar_errors/question-mark-positive.txt",
        "negative": "data/validated/grammar_errors/question-mark-negative.txt"
    },
    {
        "error": GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value,
        "positive": "data/validated/grammar_errors/plural-vs-possessive-positive.txt",
        "negative": "data/validated/grammar_errors/plural-vs-possessive-negative.txt"
    },
    {
        "error": GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value,
        "positive": "data/validated/grammar_errors/plural-vs-possessive-positive-comprehension.txt",
        "negative": "data/validated/grammar_errors/plural-vs-possessive-negative-comprehension.txt"
    },
    {
        "error": GrammarError.COMMAS_IN_NUMBERS.value,
        "positive": "data/validated/grammar_errors/commas-in-numbers-positive.txt",
        "negative": "data/validated/grammar_errors/commas-in-numbers-negative.txt"
    },
    {
        "error": GrammarError.YES_NO_COMMA.value,
        "positive": "data/validated/grammar_errors/commas-after-yes-no-positive.txt",
        "negative": "data/validated/grammar_errors/commas-after-yes-no-negative.txt"
    },
    {
        "error": GrammarError.SINGULAR_PLURAL.value,
        "positive": "data/validated/grammar_errors/singular-plural-noun-positive.txt",
        "negative": "data/validated/grammar_errors/singular-plural-noun-negative.txt"
    },
    {
        "error": GrammarError.PERFECT_WITH_INCORRECT_PARTICIPLE.value,
        "positive": "data/validated/grammar_errors/incorrect-participle-positive.txt",
        "negative": "data/validated/grammar_errors/incorrect-participle-negative.txt"
    },
    {
        "error": GrammarError.PASSIVE_WITH_INCORRECT_PARTICIPLE.value,
        "positive": "data/validated/grammar_errors/passive-with-incorrect-participle-positive.txt",
        "negative": "data/validated/grammar_errors/passive-with-incorrect-participle-negative.txt"
    },
    {
        "error": GrammarError.THAN_THEN.value,
        "positive": "data/validated/grammar_errors/than-then-positive.txt",
        "negative": "data/validated/grammar_errors/than-then-negative.txt"
    },
    {
        "error": GrammarError.PERFECT_WITHOUT_HAVE.value,
        "positive": "data/validated/grammar_errors/perfect-without-have-positive.txt",
        "negative": "data/validated/grammar_errors/perfect-without-have-negative.txt"
    },
    {
        "error": GrammarError.SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT.value,
        "positive": "data/validated/grammar_errors/simple-past-instead-of-past-perfect-positive.txt",
        "negative": "data/validated/grammar_errors/simple-past-instead-of-past-perfect-negative.txt"
    },
    {
        "error": GrammarError.PAST_TENSE_INSTEAD_OF_PARTICIPLE.value,
        "positive": "data/validated/grammar_errors/past-tense-instead-of-participle-positive.txt",
        "negative": "data/validated/grammar_errors/past-tense-instead-of-participle-negative.txt"
    },
    {
        "error": GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value,
        "positive": "data/validated/grammar_errors/perfect-progressive-without-have-positive.txt",
        "negative": "data/validated/grammar_errors/perfect-progressive-without-have-negative.txt"
    },
    {
        "error": GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE.value,
        "positive": "data/validated/grammar_errors/perfect-progressive-with-incorrect-be-and-without-have-positive.txt",
        "negative": "data/validated/grammar_errors/perfect-progressive-with-incorrect-be-and-without-have-negative.txt"
    },
    {
        "error": GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE.value,
        "negative": "data/validated/grammar_errors/perfect-progressive-with-incorrect-be-and-without-have-negative-comprehension.txt"
    },
    {
        "error": GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value,
        "positive": "data/validated/grammar_errors/passive-perfect-without-have-positive.txt",
        "negative": "data/validated/grammar_errors/passive-perfect-without-have-negative.txt"
    },
    {
        "error": GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value,
        "positive": "data/validated/grammar_errors/passive-perfect-with-incorrect-participle-positive.txt",
        "negative": "data/validated/grammar_errors/passive-perfect-with-incorrect-participle-negative.txt"
    },
    {
        "error": GrammarError.PASSIVE_WITHOUT_BE.value,
        "positive": "data/validated/grammar_errors/passive-without-be-positive.txt",
        "negative": "data/validated/grammar_errors/passive-without-be-negative.txt"
    },
    {
        "error": GrammarError.PASSIVE_WITH_INCORRECT_BE.value,
        "positive": "data/validated/grammar_errors/passive-with-incorrect-be-positive.txt",
        "negative": "data/validated/grammar_errors/passive-with-incorrect-be-negative.txt"
    },
    {
        "error": GrammarError.PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE.value,
        "positive": "data/validated/grammar_errors/passive-with-simple-past-instead-of-participle-positive.txt",
        "negative": "data/validated/grammar_errors/passive-with-simple-past-instead-of-participle-negative.txt"
    },
    {
        "error": GrammarError.SVA_SIMPLE_NOUN.value,
        "positive": "data/validated/grammar_errors/subject-verb-agreement-with-simple-noun-positive.txt",
        "negative": "data/validated/grammar_errors/subject-verb-agreement-with-simple-noun-negative.txt"
    },
    {
        "error": GrammarError.SVA_PRONOUN.value,
        "positive": "data/validated/grammar_errors/subject-verb-agreement-with-pronoun-positive.txt",
        "negative": "data/validated/grammar_errors/subject-verb-agreement-with-pronoun-negative.txt"
    },
    {
        "error": GrammarError.CONTRACTION.value,
        "positive": "data/validated/grammar_errors/contraction-positive.txt",
        "negative": "data/validated/grammar_errors/contraction-negative.txt"
    },
    {
        "error": GrammarError.PUNCTUATION.value,
        "positive": "data/validated/grammar_errors/punctuation-positive.txt",
        "negative": "data/validated/grammar_errors/punctuation-negative.txt"
    },
    {
        "error": GrammarError.ARTICLE.value,
        "positive": "data/validated/grammar_errors/article-positive.txt",
        "negative": "data/validated/grammar_errors/article-negative.txt"
    },
    {
        "error": GrammarError.IRREGULAR_PLURAL_NOUN.value,
        "positive": "data/validated/grammar_errors/irregular-plural-nouns-positive.txt",
        "negative": "data/validated/grammar_errors/irregular-plural-nouns-negative.txt"
    },
    {
        "error": GrammarError.SVA_INVERSION.value,
        "positive": "data/validated/grammar_errors/subject-verb-agreement-with-inversion-positive.txt",
        "negative": "data/validated/grammar_errors/subject-verb-agreement-with-inversion-negative.txt"
    },
    {
        "error": GrammarError.SVA_INDEFINITE.value,
        "positive": "data/validated/grammar_errors/subject-verb-agreement-with-indefinite-pronoun-positive.txt",
        "negative": "data/validated/grammar_errors/subject-verb-agreement-with-indefinite-pronoun-negative.txt"
    },
    {
        "error": GrammarError.SPACING.value,
        "positive": "data/validated/grammar_errors/spacing-positive.txt",
        "negative": "data/validated/grammar_errors/spacing-negative.txt"
    },
    {
        "error": GrammarError.SUBJECT_PRONOUN.value,
        "positive": "data/validated/grammar_errors/subject-pronouns-positive.txt",
        "negative": "data/validated/grammar_errors/subject-pronouns-negative.txt"
    },
    {
        "error": GrammarError.OBJECT_PRONOUN.value,
        "positive": "data/validated/grammar_errors/object-pronouns-positive.txt",
        "negative": "data/validated/grammar_errors/object-pronouns-negative.txt"
    },
    {
        "error": GrammarError.POSSESSIVE_PRONOUN.value,
        "positive": "data/validated/grammar_errors/possessive-pronouns-positive.txt",
        "negative": "data/validated/grammar_errors/possessive-pronouns-negative.txt"
    },
    {
        "error": GrammarError.ITS_IT_S.value,
        "positive": "data/validated/grammar_errors/its-its-positive.txt",
        "negative": "data/validated/grammar_errors/its-its-negative.txt"
    },
    {
        "error": GrammarError.SVA_SIMPLE_NOUN.value,
        "positive": "data/validated/grammar_errors/subject-verb-agreement-with-simple-noun-positive-comprehension.txt",
        "negative": "data/validated/grammar_errors/subject-verb-agreement-with-simple-noun-negative-comprehension.txt"
    }
]