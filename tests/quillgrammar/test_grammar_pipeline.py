import yaml

from quillgrammar.grammar.checks.rules import RuleBasedGrammarChecker, RepeatedConjunctionCheck
from quillgrammar.grammar.pipeline import GrammarPipeline
from quillgrammar.grammar.constants import GrammarError

config_file = "grammar_config_test.yaml"


def test_grammar_pipeline1():

    sentence = "By the time Fatma retired from the United States Navy, she'd earned 899830810830 medals!"

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    # We only want to find the "Commas in numbers" error
    assert len(errors) == 1


def test_grammar_pipeline3():

    sentence = "The construction worker, who is working right outside of our building, work all night."
    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert errors[0].type == GrammarError.SVA_SEPARATE.value


def test_grammar_pipeline4():

    sentence = "Nancy had been considering moving out of the apartment " \
               "when she finally decided to re-sign the lease with her old roommates."

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert len(errors) == 0


def test_grammar_pipeline5():

    sentence = "What kitchen appliance do you use every day"

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert errors[0].type == GrammarError.PUNCTUATION.value


def test_grammar_pipeline6():

    sentence = "It been done, the crook said."

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    errors = pipeline.check(sentence, "")

    assert errors[0].type == GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value


def test_grammar_pipeline_for_sva_no_errors():

    sentences = [("Large amounts of meat consumption are harming the environment "
                  "because it generates 30 to 50 gallons of methane daily contributing "
                  "to greenhouse gases and global warming.",
                  "Large amounts of meat consumption are harming the environment because"),
                 ('Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so it is important to recognize the dangerous '
                  'precedent that will be set by banning her work because it '
                  '"further stigmatizes and marginalizes LGBTQ youth and '
                  'fosters an atmosphere of intolerance."',
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but one advocacy group is fighting back, "
                  "claiming that the book resonates with the experiences "
                  "of many LGBT youth.",
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Large amounts of meat consumption are harming the "
                  "environment because it accumulates in the atmosphere "
                  "and traps in heat, leading to global warming.",
                  "Large amounts of meat consumption are harming the "
                  "environment because"),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, so the battle rages on between freedom of "
                  "expression and holding on to moral values.",
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Large amounts of meat consumption are harming the "
                  "environment, so Impossible Burger has developed a "
                  "plant-based burger that tastes similar to beef.",
                  "Large amounts of meat consumption are harming the "
                  "environment because"),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but advocacy groups are fighting back "
                  "because it resonates with many youth experiences.",
                  'Alison Bechdel’s memoir has been challenged in certain '
                  'communities, so'),
                 ("Large amounts of meat consumption are harming the "
                  "environment, but if they ate seaweed more often, "
                  "they would burp less.",
                  "Large amounts of meat consumption are harming the "
                  "environment because"),
#                 ("Young kids’ lives often revolve around seeing their "
#                  "friends and exploring the world, so being forced to "
#                  "shelter at home with their family can feel really "
#                  "hard.", ""),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because it was “promoting the gay and lesbian "
                  "lifestyle.”", "Alison Bechdel’s memoir has been "
                  "challenged in certain communities because"),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but memories are too pornographic for schools.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but "),
                 ("Methane from cow burps harms the environment, but it doesn't "
                  "have to be that way.",
                  "Methane from cow burps harms the environment, but "),
                 ("Plastic bag reduction laws are beneficial because it decreases "
                  "the negative effects of plastic production.",
                  "Plastic bag reduction laws are beneficial because "),
                 ("Alison Bechdel's memoir has been challenged in certain communities, "
                  "but memories are too pornographic for schools.", ""),
                 ("Large amounts of meat consumption are harming the environment, but "
                  "Impossible Foods is working on alternatives.", ""),
                 ("Large amounts of meat consumption are harming the environment, so "
                  "Impossible Foods has come up with a meat alternative that may meat "
                  "eaters actually like.", ""),
                 ("Alison Bechdel's memoir has been challenged in certain communities, but "
                  "the National Coalition Against Censorship (NCAC) has pushed back against "
                  "the attempts to ban her book.", "")]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt in sentences:
        errors = pipeline.check(sentence, prompt)

        assert len(errors) == 0


def test_grammar_pipeline_for_sva_errors():

    sentences = [("There exist another way for all of us to live.", "", "another way", 12),
                 ("That ballad, performed by the one and only Katy Perry, "
                  "am moving the audience to tears.", "", "That ballad", 0),
                 ("I are coming home.", "", "I", 0),
                 ("The island hug a turquoise lagoon rimmed with the "
                  "world’s southernmost coral reef.", "", "The island", 0),
                 ("Located at the exact point where Switzerland, France and "
                  "Germany meet, the city straddle a bend of the Rhine.", "", "the city", 71),
                 ("Plastic bag reduction laws are beneficial because it decrease "
                  "the negative effects of plastic production.",
                  "Plastic bag reduction laws are beneficial because ", "it", 50)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, subject, subject_idx in sentences:
        errors = pipeline.check(sentence, prompt)

        print(sentence)
        print(errors)

        assert len(errors) > 0
        assert "agreement" in errors[0].type
        assert errors[0].subject == subject
        assert errors[0].subject_idx == subject_idx


def test_grammar_pipeline_for_question_marks():

    sentences = [("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but it continues to resonate as a personal "
                  "coming of age story,",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities, but")]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt in sentences:
        errors = pipeline.check(sentence, prompt)

        assert len(errors) == 1
        assert errors[0].type == GrammarError.PUNCTUATION.value


def test_grammar_pipeline_for_subject_pronouns():

    sentences = [("Our mom has been fixing the sink for the past few hours, but I think it's still leaky.",
                  "", 0),
                 ("Our are going to rise up in the name of justice.", "", 1)]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        assert len(errors) == num_errors


def test_grammar_pipeline_spacing():

    sentences = [("Eastern Michigan University cut women's tennis and "
                  "softball because it faced a budget shortfall of least "
                  "$4.5 million in 2018.",
                  "", 0),
                 ("There are 1.5ish million cows.", "", 0),
                 ("Large amounts of meat consumption are harming the environment "
                  "because there are 1.5 billion cows.",
                  "", 0),
                 ("Methane from cow burps harms the environment, but it "
                  "produces about 14.5% of the world's green houses gas .",
                  "", 1),
                 ("Methane from cow burps harms the environment, but it "
                  "produces about 14.5 % of the world's green houses gas.",
                  "", 1)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_articles():

    sentences = [("Large amounts of meat consumption are harming the "
                  "environment, but an impossible burger generates 89% "
                  "fewer greenhouse gases.",
                  "Large amounts of meat consumption are harming the "
                  "environment, but ", "", 0),
                 ("What are the qualities of an good leader?",
                  "", "an good", 1)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, text, num_errors in sentences:
        errors = pipeline.check(sentence, prompt)

        print("Identified errors:", errors)
        assert len(errors) == num_errors
        if len(errors) > 0:
            assert errors[0].text == text


def test_grammar_pipeline_capitalization():

    sentences = [("Methane from cow burps harms the environment, but BY "
                  "MAKING DIFFERENT FEED CHOICES, IT WILL REDUCE EFFECTS "
                  "OF METHANE.",
                  "Methane from cow burps harms the environment, but", 1),
                 ("Methane from cow burps harms the environment, but BY "
                  "MAKING DIFFERENT FEED CHOICES, IT WILL REDUCE EFFECTS "
                  "OF METHANE.", "", 0)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_its():

    sentences = [
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because some people believe that it's "
                  "pornographic and promotes gay and lesbian lifestyle.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 0),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because of its pornographic style.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 0),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because it's pornographic.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 0),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities because of it's pornographic style.",
                  "Alison Bechdel’s memoir has been challenged in certain "
                  "communities because", 1)]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_inversion():

    sentences = [("There are only one thing you need to know about me.", "", 1)]
    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_grammar_pipeline_perfect_progressive_without_have():

    sentences = [("Large amounts of meat consumption are harming the environment "
                 "because it contributes to global warming and raising the "
                 "earth's temperature.", "", 0),
                 ("Plastic bag reduction laws are beneficial, but it can reduce "
                  "the chance of people developing illnesses.",
                  "", 0),
                 ("Large amounts of meat consumption are harming the environment, "
                  "but ending animal agriculture is more important.", "", 0),
                 ("Plastic bag reduction laws are beneficial, but people whose job "
                  "it is to produce these plastic bags fear losing their jobs.", "", 0),
                 ("He been writing fiction since he was young.", "", 1),
                 ("We been catching up on the Sopranos together each evening.", "", 1)]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_capitalization():

    sentences = [("Large amounts of meat consumption are harming the environment, "
                  "so i have linked global warming to an increase in "
                  "extreme weather events.",
                  "Large amounts of meat consumption are harming the environment,", 1)]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_initial_verb():

    sentences = [("Large amounts of meat consumption are harming the environment, "
                  "so there is no problem in this sentence.",
                  "Large amounts of meat consumption are harming the environment, so", 0),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so see there is a problem.",
                  "Large amounts of meat consumption are harming the environment, so", 1),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so reading is great.",
                  "Large amounts of meat consumption are harming the environment, so", 0),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so listening will not help.",
                  "Large amounts of meat consumption are harming the environment, so", 0),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so stopping to eat meat would be a good idea.",
                  "Large amounts of meat consumption are harming the environment, so", 0),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so ground meat is a problem, too.",
                  "Large amounts of meat consumption are harming the environment, so", 0),
                 ("Large amounts of meat consumption are harming the environment, "
                  "so learned behavior should do the trick.",
                  "Large amounts of meat consumption are harming the environment, so", 0)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, num_errors in sentences:
        errors = set([e.type for e in pipeline.check(sentence, prompt)])

        print(sentence)
        print("Identified errors:", errors)
        assert len(errors) == num_errors


def test_repeated_conjunction_check():

    sentences = [("The climate is changing because because we eat too much meat.",
                  "The climate is changing because", "because", 32),
                 ("The climate is changing so so we should eat less meat.",
                  "The climate is changing so", "so", 27),
                 ("The climate is changing, but but we can't eat less meat.",
                  "The climate is changing, but", "but", 29),
                 ("The climate is changing, but we can't eat less meat.",
                  "The climate is changing, but", "", 0),
                 ("The climate is changing, but it's always been hot.",
                  "The climate is changing, but", "", 0),
                 ("Alison Bechdel’s memoir has been challenged in certain "
                  "communities, so so  that leaves the question 'Should it "
                  "be banned?'", "Alison Bechdel’s memoir has been challenged "
                  "in certain communities, so", "so", 71)
                 ]

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) > 0
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == GrammarError.REPEATED_CONJUNCTION.value
        else:
            assert len(errors) == 0


def test_capitalization_check():

    sentences = [("Methane from cow burps harms the environment because it contributes to global warming.",
                  "Methane from cow burps harms the environment because", "", 0, None),
                 ("Methane from cow burps harms the environment because IT CONTRIBUTES TO GLOBAL WARMING.",
                  "Methane from cow burps harms the environment because", "IT CONTRIBUTES TO GLOBAL WARMING.", 52,
                  GrammarError.ALLCAPS.value)]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_possessive_pronouns_plural_possessive():

    sentences = [("Large amounts of meat consumption are harming the "
                  "environment, but introducing seaweed to cows diets "
                  "can help reduce the amount of methane that they "
                  "produce up to 99%.", "", "cows", 90, GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value)]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_plural_possessive():

    sentences = [
        ("We went to my fathers house.", "", "", 0, None),
        ("Large amounts of meat consumption are harming the "
         "environment, so we should feed the cows seaweed.",
         "Large amounts of meat consumption are harming the "
         "environment, so ", "", 0, None)
    ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_starts_with_verb():

    sentences = [("Methane from cow burps harms the environment, so can "
                  "the GMO chemicals used to produce the impossable burger.",
                  "Methane from cow burps harms the environment, so", "", 0, None),
                 ("Plastic bag reduction laws are beneficial, so can help protect "
                  "the health of communities located closest to these plants.",
                  "Plastic bag reduction laws are beneficial, so", "can",
                  46, GrammarError.RESPONSE_STARTS_WITH_VERB.value)]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_plurals():

    sentences = [("There are two persons.", "", "persons", 14,
                  GrammarError.PERSONS.value),
                 ("There are two gasses.", "", "gasses", 14,
                  GrammarError.GASSES.value),
                 ("There are two peoples' cars.", "", "peoples'", 14,
                  GrammarError.PEOPLES_APOSTROPHE.value),
                 ("There are two peoples.", "", "peoples", 14,
                  GrammarError.PEOPLES.value),
                 ("There are two monies in the car.", "", "monies", 14,
                  GrammarError.MONIES.value),
                 ("There are two in regards to.", "", "in regards to", 14,
                  GrammarError.IN_REGARDS_TO.value)
                 ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)

        if index > 0:
            assert len(errors) > 0
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_decades():

    sentences = [("I was born in the 1980's.", "", "1980's", 18,
                  GrammarError.DECADES_WITH_APOSTROPHE.value),
                 ("I was born in the 1980s.", "", "", 0, None)
                 ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 2
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_irregular_plural_nouns():

    sentences = [("Plastic bag reduction laws are beneficial, so "
                  "that less micro-plastics are released into the "
                  "air and water systems, which in turn protects us "
                  "all.", "", "", 0, None),
                 ("Large amounts of meat consumption are harming the "
                  "environment, so the solution lies in what farmers "
                  "feed cows- seaweed would be a better food.", "",
                  "", 0, None),
                 ("Methane from cow burps harms the environment, so "
                  "we should try to find ways to prevent that like "
                  "feeding cows seaweed which helps them release 99%"
                  " less methane in their burps.", "",
                  "", 0, None)]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_singular_plural():

    sentences = [
#                  ("Large amounts of meat consumption are harming the "
#                  "environment because methane is a greenhouse-gas, "
#                  "excessive amounts of which contributes to global "
#                  "warming.", "Large amounts of meat consumption are "
#                  "harming the environment because", "", 0, None),
                 ("Large amounts of meat consumption are harming the "
                  "environment, so one way or another governments need "
                  "to recognize this threat and invest in a reasonable "
                  "solution.", "Large amounts of meat consumption are "
                  "harming the environment because", "", 0, None),
                 ("I have a good friends.", "", "a good friends",
                  7, GrammarError.SINGULAR_PLURAL.value),
    ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_some_more():
    sentences = [
        ("I'm sorry to tell you this, but I think those shoes you "
         "wanted been bought by somebody else yesterday.", "",
         "", 0, None)
    ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > 0:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_contractions():

    sentences = [
        ("Theyll come and go.", "", "Theyll", 0, GrammarError.CONTRACTION.value)
    ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > -1:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0


def test_repeated_word():

    sentences = [
        ("I love love you.", "", "love love", 2, GrammarError.REPEATED_WORD.value)
    ]

    with open("grammar_config_test.yaml") as i:
        config = yaml.load(i)

    pipeline = GrammarPipeline(config)

    for sentence, prompt, word, index, error_type in sentences:
        errors = pipeline.check(sentence, prompt)
        print(errors)

        if index > -1:
            assert len(errors) == 1
            assert errors[0].text == word
            assert errors[0].index == index
            assert errors[0].type == error_type
        else:
            assert len(errors) == 0
