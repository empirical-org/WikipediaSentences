import pkg_resources
from symspellpy import SymSpell, Verbosity

import spacy
nlp = spacy.load("en")


sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt")
bigram_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_bigramdictionary_en_243_342.txt")
# term_index is the column of the term and count_index is the
# column of the term frequency
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

s = sym_spell.lookup("practiced", Verbosity.CLOSEST, max_edit_distance=2, transfer_casing=True,
                                               include_unknown=True)

print([sug.term for sug in s])
input()

corrected = 0
with open("scored_data.txt") as i, open("results_symspell_lookup.txt", "w") as o:

    for line in i:
        line = line.strip()
        tokens = [t for t in nlp(line.strip())]

        new_tokens = []
        for t in tokens:
            if t.text.isalpha():
                suggestions = sym_spell.lookup(t.text, Verbosity.CLOSEST, max_edit_distance=2,
                                               transfer_casing=True,
                                               include_unknown=True)
                if len(suggestions) > 0:
                    replacement = suggestions[0].term
                    new_tokens.append(replacement + t.whitespace_)
                else:
                    new_tokens.append(t.text_with_ws)
            else:
                new_tokens.append(t.text_with_ws)

        corrected_sentence = "".join(new_tokens)

        if not line.strip().startswith(corrected_sentence):
            o.write(corrected_sentence + "\n")
            corrected += 1
        else:
            o.write("\n")

print(corrected)
