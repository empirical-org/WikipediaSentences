from quillgrammar.grammar.constants import GrammarError, Tag, POS
from quillnlp.grammar.generation import ErrorGenerator


class SimplePastInsteadOfPastPerfectErrorGenerator(ErrorGenerator):

    name = GrammarError.SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT.value

    def generate_from_doc(self, doc):

        tags = set([t.tag_ for t in doc])
        if Tag.PAST_PARTICIPLE_VERB.value not in tags:
            return doc.text, []

        for token in doc:
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and token.pos_ == POS.VERB.value:
                negations = [t for t in token.lefts if t.text.lower() == "n't" or t.text.lower() == "not"]
                if len(negations) > 0:
                    break
                auxiliaries = [t for t in token.lefts if (t.pos_ == POS.AUX.value or t.pos_ == POS.VERB.value)]
                if len(auxiliaries) == 1 and auxiliaries[0].text.lower() == "had":
                    auxiliaries[0]._.replace = ""
                    new_form = token._.inflect("VBD")
                    if new_form is not None:
                        token._.replace = new_form
                        break

        new_sentence = ""
        entities = []
        for token in doc:
            if token._.replace == "":
                continue
            elif token._.replace:
                start_idx = len(new_sentence)
                new_sentence += token._.replace + token.whitespace_
                entities.append([start_idx, start_idx + len(token._.replace), self.name])
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SimplePastInsteadOfPresentPerfectErrorGenerator(ErrorGenerator):

    name = GrammarError.SIMPLE_PAST_INSTEAD_OF_PRESENT_PERFECT.value

    def generate_from_doc(self, doc):

        tags = set([t.tag_ for t in doc])
        if Tag.PAST_PARTICIPLE_VERB.value not in tags:
            return doc.text, []

        for token in doc:
            if token.tag_ == Tag.PAST_PARTICIPLE_VERB.value and token.pos_ == POS.VERB.value:
                negations = [t for t in token.lefts if t.text.lower() == "n't" or t.text.lower() == "not"]
                if len(negations) > 0:
                    break
                auxiliaries = [t for t in token.lefts if (t.pos_ == POS.AUX.value or t.pos_ == POS.VERB.value)]
                if len(auxiliaries) == 1 and \
                        (auxiliaries[0].text.lower() == "have" or auxiliaries[0].text.lower() == "has"):
                    auxiliaries[0]._.replace = ""
                    new_form = token._.inflect("VBD")
                    if new_form is not None:
                        token._.replace = new_form
                        break

        new_sentence = ""
        entities = []
        for token in doc:
            if token._.replace == "":
                continue
            elif token._.replace:
                start_idx = len(new_sentence)
                new_sentence += token._.replace + token.whitespace_
                entities.append([start_idx, start_idx + len(token._.replace), self.name])
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities
