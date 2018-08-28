import os
import csv
import textacy
from pattern.en import conjugate,tenses
from .reducer_helper import get_reduction, load_predictor
from .alt_sentences import get_alt_sentences

# Load reduction_counts dictionary
__location__ = os.path.dirname(__file__)
with open(os.path.join(__location__, 'data', 'reduction_counts.csv'), 'r') as infile:
    csv_reader = csv.DictReader(infile)
    reduction_dict = {row['reduction']:int(row['count']) for row in csv_reader}
num_reductions = sum(reduction_dict.values())

# Load AllenNLP Model
predictor = load_predictor(path="/var/lib/allennlp/elmo-constituency-parser-2018.03.14.tar.gz")

class Feedback(object):
    """Result feedback class"""
    def __init__(self):
        self.human_readable = '' # human readable advice
        self.primary_error = None
        self.specific_error = None
        self.matches = {}        # possible errors

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return self.human_readable

def get_feedback(sentence):
    result = Feedback()
    alt_sentences = get_alt_sentences(sentence)
    reductions = get_reduction(sentence, predictor)
    if not reductions:
        return None # No reductions, no response
    reduction_counts = [get_count(r) for r in reductions]
    score = sum(reduction_counts)
    alt_score = 0
    suggestion = "< no suggestion >"
    for alt_s in alt_sentences:
        areductions = get_reduction(alt_s, predictor)
        reduction_counts = [get_count(r) for r in areductions]
        if sum(reduction_counts) > alt_score:
            alt_score = sum(reduction_counts)
            suggestion = alt_s
    if alt_score > score:
        correct =  False
    elif score == 0:
        correct = False
    else:
        correct = True

    if not correct:
        result = "That looks like a subject verb agreement error.\n suggestion: {}".format(suggestion)
    else:
        result = None
    return result

def get_count(reduction):
    """Returns frequency of reduction in training data
    Return value is between 0 and 1, scaled by total number of reductions
    Returns 0 if no reduction found in dict
    """
    return reduction_dict.get(reduction, 0)/num_reductions

def get_tense_and_aspect(verb):
    t = tenses(verb)
    for tx in t:
        if tx[0] and tx[4]:
            return (tx[0], tx[4])
    return (None, None)
