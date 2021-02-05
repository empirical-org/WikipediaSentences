import random

import lemminflect

from quillgrammar.grammar.constants import Tag, GrammarError, Dependency, POS, TokenSet
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.verbutils import get_subject, get_plural, is_indefinite, has_noun_subject, \
    is_negated_with_contraction, has_following_subject, subject_has_neither, subject_has_either, has_pronoun_subject


class SubjectVerbAgreementWithSimpleNounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_SIMPLE_NOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif has_noun_subject(token) and not is_negated_with_contraction(token, doc):

                # singular -> plural
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token.lemma_
                        new_form = new_form.title() if token.text.istitle() else new_form

                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx+len(new_form), self.name))

                # plural -> singular
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "is", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)

                    if new_form is not None:
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx+len(new_form), self.name))
                    else:
                        new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithPronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_PRONOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws

            elif has_pronoun_subject(token) and not is_negated_with_contraction(token, doc):

                # third-person singular -> other form
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                    else:
                        new_form = token.lemma_
                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx+len(new_form), self.name))

                # other form -> third-person form
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        other_forms = set(["be", "are", "am", "is"]) - set(token.text.lower())
                        new_form = random.choice(list(other_forms))
                        new_form = new_form.title() if token.text.istitle() else new_form
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx + len(new_form), self.name))
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                        if new_form is not None:
                            new_sentence += new_form + token.whitespace_
                            entities.append((token.idx, token.idx + len(new_form), self.name))
                        else:
                            new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementErrorGenerator(ErrorGenerator):

    name = GrammarError.SUBJECT_VERB_AGREEMENT.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            else:
                # singular -> plural
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token.lemma_
                        new_form = new_form.title() if token.text.istitle() else new_form

                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx+len(new_form), self.name))

                # plural -> singular
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "is", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)

                    if new_form is not None:
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx+len(new_form), self.name))
                    else:
                        new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws

        return new_sentence, entities


class IncorrectThirdPersonWithNegationErrorGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_NEGATIVE_VERB_WITH_A_SIMPLE_NOUN_SUBJECT.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and \
                    is_negated_with_contraction(token, doc) and \
                    has_noun_subject(token):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_form = new_form.title() if token.text.istitle() else new_form
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithInversionErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_INVERSION.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif (token.tag_ == Tag.PRESENT_SING3_VERB.value or token.tag_ == Tag.PRESENT_OTHER_VERB.value) and \
                    has_following_subject(token):
                # third-person singular -> other form
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        # most confusion will be between is and are, so are gets highest probability
                        new_form = random.choice(["be", "am", "are", "are", "are"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token.lemma_
                        new_form = new_form.title() if token.text.istitle() else new_form
                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx + len(new_form), self.name))

                # other form -> third-person form
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        other_forms = set(["be", "are", "am", "is"]) - set(token.text.lower())
                        other_forms = list(other_forms)
                        if "is" in other_forms:
                            other_forms.extend(["is", "is", "is"])
                        new_form = random.choice(other_forms)
                        new_form = new_form.title() if token.text.istitle() else new_form
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx + len(new_form), self.name))
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                        if new_form is not None:
                            new_sentence += new_form + token.whitespace_
                            entities.append((token.idx, token.idx + len(new_form), self.name))
                        else:
                            new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithNeitherNorErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_NEITHER_NOR.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and subject_has_neither(token):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and subject_has_neither(token):
                new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx + len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithEitherOrErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_EITHER_OR.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and subject_has_either(token, doc):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and subject_has_either(token, doc):
                new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx + len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithCollectiveNoun(ErrorGenerator):

    name = GrammarError.SVA_COLLECTIVE_NOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                subject = get_subject(token)
                if subject is not None and subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                    plural = get_plural(token)
                    new_sentence += plural + token.whitespace_
                    entities.append((token.idx, token.idx + len(plural), self.name))
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithIndefinitePronoun(ErrorGenerator):

    name = GrammarError.SVA_INDEFINITE.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []

        for token in doc:
            if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                subject = get_subject(token)
                if subject is not None and is_indefinite(subject):
                    plural = get_plural(token)
                    new_sentence += plural + token.whitespace_
                    entities.append((token.idx, token.idx + len(plural), self.name))
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities