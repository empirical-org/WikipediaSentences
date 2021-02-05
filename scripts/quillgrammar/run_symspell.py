import pkg_resources
from symspellpy import SymSpell, Verbosity


sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt")
bigram_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_bigramdictionary_en_243_342.txt")
# term_index is the column of the term and count_index is the
# column of the term frequency
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)


corrected = 0
with open("scored_data.txt") as i, open("results_symspell.txt", "w") as o:

    for line in i:
        line = line.strip()

        # lookup suggestions for multi-word input strings (supports compound
        # splitting & merging)
        # max edit distance per lookup (per single word, not per whole input string)
        suggestions = sym_spell.lookup_compound(line, max_edit_distance=2, transfer_casing=True)
        # display suggestion term, edit distance, and term frequency

        for suggestion in suggestions:
            corrected_sentence = suggestion.term
            break

        if not line.strip().startswith(corrected_sentence):
            o.write(corrected_sentence + "\n")
            corrected += 1
        else:
            o.write("\n")

print(corrected)
