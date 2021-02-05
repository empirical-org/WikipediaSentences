import re

from quillgrammar.grammar.constants import GrammarError, Tag, Dependency
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.verbutils import get_perfect_progressives, in_have_been_construction, is_passive


class PerfectTenseWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_WITHOUT_HAVE.value

    def generate_from_doc(self, doc):

        # This method should affect "I have been here", but not "I have been working here".
        # The difference between the two is that with spaCy, "been" in the first
        # sentence is the ROOT and has left children. In the second sentence, "working"
        # is the root and "been" has no left children.

        tags = [t.tag_ for t in doc]
        if Tag.PAST_PARTICIPLE_VERB.value not in tags:
            return doc.text, []

        for token in doc:
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and not is_passive(token):

                # We ensure the past tense is different from the past participle.
                # Otherwise removing 'have' may not result in an error.
                past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
                present_tense = token._.inflect(Tag.PRESENT_OTHER_VERB.value)
                participle = token._.inflect(Tag.PAST_PARTICIPLE_VERB.value)

                if past_tense is not None and \
                        participle is not None and \
                        present_tense is not None and \
                        past_tense != participle and \
                        present_tense != participle:
                    for child in token.lefts:
                        if child.dep_ == Dependency.AUX.value and child.lemma_ == "have":
                            child._.replace = " " if child.text.startswith("'") else ""

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) == 0 and token._.replace is not None:
                new_sentence += token._.replace
                next_token = doc[token.i+1]
                entities.append([next_token.idx - len(token.text_with_ws) + len(token._.replace),
                                 next_token.idx - len(token.text_with_ws) + len(token._.replace) + len(next_token),
                                 self.name])
            else:
                new_sentence += token.text_with_ws

        # She n't broken the record => She not broken the record.
        new_sentence = re.sub("\sn't", " not", new_sentence)

        return new_sentence, entities


class PerfectProgressiveWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value

    def generate_from_doc(self, doc):

        # In contrast to the method above,
        # this method should affect "I have been working here", but not "I have been here".
        # See above how this can be done.
        # The checks that the participle differs from the past/present tense
        # are not needed here, because removing have from a perfect progressive will
        # always result in an error.

        tags = [t.tag_ for t in doc]
        if Tag.PRESENT_PARTICIPLE_VERB.value not in tags:
            return doc.text, []

        for token in doc:
            if token.tag_ == Tag.PRESENT_PARTICIPLE_VERB.value and not is_passive(token):
                for child in token.lefts:
                    if child.dep_ == Dependency.AUX.value and child.lemma_ == "have":
                        child._.replace = " " if child.text.startswith("'") else ""

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) == 0 and token._.replace is not None:
                new_sentence += token._.replace
                next_token = doc[token.i+1]
                entities.append([next_token.idx - len(token.text_with_ws) + len(token._.replace),
                                 next_token.idx - len(token.text_with_ws) + len(token._.replace) + len(next_token),
                                 self.name])
            else:
                new_sentence += token.text_with_ws

        # She n't broken the record => She not broken the record.
        new_sentence = re.sub("\sn't", " not", new_sentence)

        return new_sentence, entities


class PassivePerfectWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value

    def generate_from_doc(self, doc):

        # Only difference with PerfectTenseWithoutHaveErrorGenerator is that here the VBN
        # should be part of a passive construction.

        tags = [t.tag_ for t in doc]
        if Tag.PAST_PARTICIPLE_VERB.value not in tags:
            return doc.text, []

        for token in doc:
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and is_passive(token):

                # We ensure the past tense is different from the past participle.
                # Otherwise removing 'have' may not result in an error.
                past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)
                present_tense = token._.inflect(Tag.PRESENT_OTHER_VERB.value)
                participle = token._.inflect(Tag.PAST_PARTICIPLE_VERB.value)

                if past_tense is not None and \
                        participle is not None and \
                        present_tense is not None and \
                        past_tense != participle and \
                        present_tense != participle:
                    for child in token.lefts:
                        if child.dep_ == Dependency.AUX.value and child.lemma_ == "have":
                            child._.replace = " " if child.text.startswith("'") else ""

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) == 0 and token._.replace is not None:
                new_sentence += token._.replace
                next_token = doc[token.i+1]
                entities.append([next_token.idx - len(token.text_with_ws) + len(token._.replace),
                                 next_token.idx - len(token.text_with_ws) + len(token._.replace) + len(next_token),
                                 self.name])
            else:
                new_sentence += token.text_with_ws

        # She n't broken the record => She not broken the record.
        new_sentence = re.sub("\sn't", " not", new_sentence)

        return new_sentence, entities


class PerfectTenseWithSimplePastErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_TENSE_WITH_INCORRECT_PARTICIPLE.value

    def generate_from_doc(self, doc):
        """ Replaces the past participle (e.g. forgotten) by the past tense (e.g. forgot) """

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws

            elif not is_passive(token) and not token.lemma_ == "be" and \
                    token.tag_ == Tag.PAST_PARTICIPLE_VERB.value:
                simple_past = token._.inflect(Tag.SIMPLE_PAST_VERB.value)

                # We only do this for verbs whose simple past does not end in "ed"
                if simple_past is not None and simple_past != token.text:
                    new_sentence += simple_past + token.whitespace_
                    entities.append([token.idx,
                                     token.idx + len(simple_past),
                                     self.name])
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class PerfectProgressiveWithIncorrectBeAndWithoutHaveErrorGenerator(ErrorGenerator):

    name = GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE.value

    def generate_from_doc(self, doc):

        perfect_progressives = get_perfect_progressives(doc)

        if len(perfect_progressives) > 0:

            first_perfect_progressive = perfect_progressives[0]

            for token in first_perfect_progressive.lefts:
                if token.lemma_ == "have":
                    token._.replace = " " if token.text.startswith("'") else ""
                elif token.text == "been":
                    token._.replace = "be"

            new_sentence = ""
            entities = []
            for token in doc:
                if token._.replace is not None and token.lemma_ == "have":
                    new_sentence += token._.replace
                elif token._.replace is not None:
                    entity_start = len(new_sentence)
                    entity_end = entity_start + len(token._.replace)
                    new_sentence += token._.replace + token.whitespace_
                    entities.append([entity_start, entity_end, self.name])
                else:
                    new_sentence += token.text_with_ws

            return new_sentence, entities

        else:
            return doc.text, []


class PassivePerfectWithIncorrectParticipleErrorGenerator(ErrorGenerator):

    name = GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value

    def generate_from_doc(self, doc):

        # Only difference with PerfectTenseWithoutHaveErrorGenerator is that here the VBN
        # should be part of a passive construction.

        tags = [t.tag_ for t in doc]
        if Tag.PAST_PARTICIPLE_VERB.value not in tags:
            return doc.text, []

        new_sentence = ""
        entities = []
        for token in doc:
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and is_passive(token) and in_have_been_construction(token):

                # We ensure the past tense is different from the past participle.
                past_tense = token._.inflect(Tag.SIMPLE_PAST_VERB.value)

                if past_tense is not None and past_tense.lower() != token.text.lower():
                    start_idx = len(new_sentence)
                    new_sentence += past_tense + token.whitespace_
                    entities.append([start_idx,
                                     start_idx + len(past_tense),
                                     self.name])

                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        # She n't broken the record => She not broken the record.
        new_sentence = re.sub("\sn't", " not", new_sentence)
        return new_sentence, entities

