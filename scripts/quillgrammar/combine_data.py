import glob
import csv
import os

from quillgrammar.grammar.constants import GrammarError

files = glob.glob("data/validated/grammar_errors/*.txt")

error_map = {
    "passive perfect without have": GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value,
    "commas after yes no": GrammarError.YES_NO_COMMA.value,
    "object pronouns": GrammarError.OBJECT_PRONOUN.value,
    "subject verb agreement with collective noun": GrammarError.SVA_COLLECTIVE_NOUN.value,
    "subject verb agreement with pronoun": GrammarError.SVA_PRONOUN.value,
    "than then": GrammarError.THAN_THEN.value,
    "passive with simple past instead of participle": GrammarError.PASSIVE_PAST_TENSE_AS_PARTICIPLE.value,
    "passive perfect with incorrect participle": GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value,
    "simple past instead of past perfect": GrammarError.VERB_SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT.value,
    "perfect without have": GrammarError.PERFECT_TENSE_WITHOUT_HAVE.value,
    "possessive pronouns": GrammarError.POSSESSIVE_PRONOUN.value,
    "subject pronouns": GrammarError.SUBJECT_PRONOUN.value,
    "passive without be": GrammarError.PASSIVE_WITHOUT_BE.value,
    "capitalization": GrammarError.CAPITALIZATION.value,
    "repeated word": GrammarError.REPEATED_WORD.value,
    "subject verb agreement with simple noun": GrammarError.SVA_SIMPLE_NOUN.value,
    "punctuation": GrammarError.PUNCTUATION.value,
    "woman women": GrammarError.WOMAN_WOMEN.value,
    "perfect progressive without have": GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value,
    "passive with incorrect participle": GrammarError.PASSIVE_WITH_INCORRECT_PARTICIPLE.value,
    "perfect progressive with incorrect be and without have": GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_WITHOUT_HAVE.value,
    "article": GrammarError.ARTICLE.value,
    "incorrect irregular past tense": GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value,
    "subject verb agreement with inversion": GrammarError.SVA_INVERSION.value,
    "passive with incorrect be": GrammarError.PASSIVE_WITH_INCORRECT_BE.value,
    "incorrect participle": GrammarError.PERFECT_WITH_INCORRECT_PARTICIPLE.value,
    "spacing": GrammarError.SPACING.value,
    "question mark": GrammarError.QUESTION_MARK.value,
    "man men": GrammarError.MAN_MEN.value,
    "contraction": GrammarError.CONTRACTION.value,
    "commas in numbers": GrammarError.COMMAS_IN_NUMBERS.value,
    "subject verb agreement with indefinite pronoun": GrammarError.SVA_INDEFINITE.value,
    "singular plural noun": GrammarError.SINGULAR_PLURAL.value,
    "plural vs possessive": GrammarError.PLURAL_POSSESSIVE.value,
    "past tense instead of participle": GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value,
    "irregular plural nouns": GrammarError.IRREGULAR_PLURAL_NOUN.value
}


def combine_error_data():
    with open("grammar_errors.csv", "w") as o:
        csv_writer = csv.writer(o, delimiter=",")

        for f in files:
            print(f)
            error_type = " ".join(os.path.basename(f).split("-")[:-1])
            if error_type not in error_map:
                continue

            if "positive" in f:
                error_type = error_map.get(error_type)
            else:
                error_type = ""

            with open(f) as i:
                for line in i:
                    csv_writer.writerow([line.strip(), error_type])


def combine_turk_data():

    data_path = "data/raw/"

    files = [("Schools should not allow junk food to be sold on campus, so", "junkfood_so2.tsv"),
             ("Schools should not allow junk food to be sold on campus, but", "junkfood_but2.tsv"),
             ("Schools should not allow junk food to be sold on campus because", "junkfood_because2.tsv"),
             ("Large amounts of meat consumption are harming the environment, but", "eatingmeat4_but.tsv"),
             ("Large amounts of meat consumption are harming the environment, so", "eatingmeat4_so.tsv"),
             ("Large amounts of meat consumption are harming the environment because", "eatingmeat4_because.tsv"),
             ("Eastern Michigan University cut women's tennis and softball, so", "title9_so.tsv"),
             ("Eastern Michigan University cut women's tennis and softball, but", "title9_but.tsv"),
             ("Eastern Michigan University cut women's tennis and softball", "title9_because.tsv"),
             ("Methane from cow burps harms the environment, so", "methane_so.tsv"),
             ("Methane from cow burps harms the environment, but", "methane_but.tsv"),
             ("Methane from cow burps harms the environment because", "methane_because.tsv"),
             ("Plastic bag reduction laws are beneficial, but", "plastic_bags_but.tsv"),
             ("Plastic bag reduction laws are beneficial, so", "plastic_bags_so.tsv"),
             ("Plastic bag reduction laws are beneficial because", "plastic_bags_because.tsv"),
             ("Alison Bechdel’s memoir has been challenged in certain communities,", "censorship_so.tsv"),
             ("Alison Bechdel’s memoir has been challenged in certain communities,", "censorship_but.tsv"),
             ("Alison Bechdel’s memoir has been challenged in certain communities", "censorship_because.tsv")
     ]

    done = set()
    with open("combined_turk_data.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        for (prompt, filename) in files:
            first = True
            full_filename = os.path.join(data_path, filename)
            with open(full_filename) as i:
                for line in i:
                    line = line.strip().split("\t")
                    sentence = line[0].strip()
                    if not sentence.startswith(prompt):
                        sentence = prompt + " " + sentence

                    if first:
                        print(sentence)
                        first = False
                    if sentence not in done:
                        writer.writerow([sentence, prompt, ""])
                        done.add(sentence)


combine_turk_data()
