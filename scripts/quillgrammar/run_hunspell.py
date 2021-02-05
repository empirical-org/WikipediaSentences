import spacy
from hunspell import Hunspell

h = Hunspell()

nlp = spacy.load("en")

corrected = 0
with open("sentences_spreadsheet.txt") as i, open("grammar_hunspell.txt", "w") as o:

    for line in i:
        tokens = [t for t in nlp(line.strip())]

        new_tokens = []
        for t in tokens:

            try:
                in_dictionary = h.spell(t.text)
            except UnicodeEncodeError:
                in_dictionary = True

            if not t.text.isalpha():
                in_dictionary = True  # do not replace , or ?

            if not in_dictionary:
                suggestions = h.suggest(t.text)
                if len(suggestions) > 0:
                    replacement = suggestions[0]
                    new_tokens.append(replacement + t.whitespace_)
                else:
                    new_tokens.append(t.text_with_ws)
            else:
                new_tokens.append(t.text_with_ws)

        corrected_sentence = "".join(new_tokens)

        if corrected_sentence != line.strip():
            o.write(corrected_sentence + "\n")
            corrected += 1
        else:
            o.write("\n")

print(corrected)
