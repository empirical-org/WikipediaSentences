import csv
import re
import torch

from typing import Dict, List, Tuple
from tqdm import tqdm

from scipy import spatial
from sklearn.cluster import KMeans
from allennlp.predictors.predictor import Predictor
from transformers.tokenization_bert import BertTokenizer
from transformers.modeling_bert import BertModel
from sentence_transformers import SentenceTransformer


from quillgrammar.grammar.checks.rules import ResponseStartsWithVerbCheck
from quillnlp.grammar.myspacy import nlp
from quillnlp.preprocessing.checks import SoResponseStartsWithThatCheck, SentenceEndsInQuestionMarkCheck, \
    MultipleSentencesCheck, ProfanityCheck, perform_check
from quillnlp.utils import detokenize, tokenize
from quillnlp.preprocessing.coref import get_coreference_dictionary
from quillopinion.opinioncheck import OpinionCheck


VERB_MAP = {"s": "be",
            "is": "be",
            "'s": "be",
            "are": "be",
            "ca": "can",
            "wo": "will",
            "has": "have"}

SUBJECTS_TO_IGNORE = set(["I", "some", "some people"])

MODAL_VERBS = set(["will", "shall", "may", "might", "can", "could", "must", "ought",
                   "should", "would", "used to", "need"])

AUX_VERBS = set(["be", "is", "were", "was", "been", "do", "does", "have", "has", "had"])

opinion_check = OpinionCheck()
verb_check = ResponseStartsWithVerbCheck()
so_response_starts_with_that_check = SoResponseStartsWithThatCheck()
ends_in_question_mark_check = SentenceEndsInQuestionMarkCheck()
multiple_sentences_check = MultipleSentencesCheck()
profanity_check = ProfanityCheck()

sentence_bert_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

MIN_SENTENCE_LENGTH = 3
MAX_SENTENCE_LENGTH = 100


class Response:

    def __init__(self, srl_output, prompt):

        self.prompt = prompt
        self.srl_output = srl_output

        self.sentence = srl_output["sentence"]
        self.response = srl_output["response"]

        sentence_length = len(nlp(srl_output["response"]))
        self.too_short = sentence_length < MIN_SENTENCE_LENGTH
        self.too_long = sentence_length > MAX_SENTENCE_LENGTH

        self.opinion = perform_check(opinion_check, srl_output["sentence"], prompt, "")
        self.starts_with_verb = perform_check(verb_check, srl_output["sentence"], prompt, "")
        self.so_response_starts_with_that = perform_check(so_response_starts_with_that_check,
                                                         srl_output["sentence"], prompt, "")
        self.ends_in_question_mark = perform_check(ends_in_question_mark_check,
                                                  srl_output["sentence"], prompt, "")
        self.profanity = perform_check(profanity_check, srl_output["sentence"], prompt, "")
        self.multiple_sentences = perform_check(multiple_sentences_check, srl_output["srl"]["words"],
                                               prompt, "")
        self.cluster = None
        self.similarity = None
        self.verb_string = None
        self.arg0_string = None
        self.arg0_antecedent = None
        self.arg1_string = None
        self.arg2_string = None
        self.modal_is_present = None
        self.auxiliary_is_present = None

    def tsv_columns(self):
        columns = ["response", "opinion", "starts with verb",
                   "so response starts with that", "ends in question mark",
                   "profanity", "multiple sentences", "too short", "too long",
                   "cluster", "similarity", "modal", "auxiliary",
                   "main verb", "extracted arg0", "intended arg0", "arg1", "arg2"]
        return columns

    def to_tsv(self):
        values = [self.response, self.opinion, self.starts_with_verb,
                  self.so_response_starts_with_that, self.ends_in_question_mark,
                  self.profanity, self.multiple_sentences, self.too_short, self.too_long,
                  self.cluster, self.similarity, self.modal_is_present, self.auxiliary_is_present,
                  self.verb_string, self.arg0_string, self.arg0_antecedent,
                  self.arg1_string, self.arg2_string]
        return values

    def parse_sentence(self):

        if "disrupt the spawning seasin" in self.srl_output["sentence"]:
            print(self.srl_output)

        corefs = get_coreference_dictionary(self.srl_output["sentence"])
        num_verbs_prompt = get_number_of_verbs_in_prompt(self.prompt, self.srl_output)
        auxiliaries = []
        modal_is_present = False
        auxiliary_is_present = False
        for verb_idx, verb in enumerate(self.srl_output["srl"]["verbs"]):

            # Skip verbs in the prompt
            if verb_idx < num_verbs_prompt:
                continue

            # Skip modals and auxiliaries, which distinguish themselves by not having
            # any arguments
            elif "[ARG" not in verb["description"]:
                if verb["verb"] in AUX_VERBS:
                    auxiliaries.append(verb["verb"])
                continue

            # 3.2.1 Preprocess the verb using a few simple rules, e.g. ca => can, etc.
            verb_string = verb["verb"].lower()
            verb_string = VERB_MAP.get(verb_string, verb_string)

            # Modal verbs can be identified as ARGM-MOD

            modal = find_modal(verb)
            if modal is not None:
                modal_is_present = True
                verb_string = f"{verb_string} ({modal})"

            if auxiliaries:
                auxiliary_is_present = True
                auxiliaries = [VERB_MAP.get(a, a) for a in auxiliaries]
                verb_string = f"{verb_string} ({', '.join(auxiliaries)})"

            # 3.2.4 If the verb is not a modal or auxiliary, identify the arguments in the sentence
            arg0_string, arg0_indices = identify_argument(verb, 0, self.srl_output["srl"]["words"])
            arg1_string, arg1_indices = identify_argument(verb, 1, self.srl_output["srl"]["words"])
            arg2_string, arg2_indices = identify_argument(verb, 2, self.srl_output["srl"]["words"])

            # If arg0 is in the coreference dictionary, identify its antecedent (the "implied subject").
            # If not, take the arg0 itself as "implied subject".
            arg0_location = "-".join([str(x) for x in arg0_indices])
            if arg0_location in corefs:
                arg0_antecedent = corefs[arg0_location]
            elif arg0_string != "-":
                arg0_antecedent = arg0_string
            else:  # These are cases where the subject is "-", as in copula verbs
                arg0_antecedent = arg1_string
                arg0_string = arg1_string
                arg1_string = "-"

            if "disrupt the spawning seasin" in self.srl_output["sentence"]:
                print(verb)

                print(arg0_string)
                print(arg1_string)

            # Add the verb information to the sentence information.
            # Exclude constructions like "I think", "I guess", etc. on the basis of a
            # list of subjects we want to ignore.

            if arg0_string not in SUBJECTS_TO_IGNORE:
                self.verb_string = verb_string
                self.arg0_string = arg0_string
                self.arg0_antecedent = arg0_antecedent
                self.arg1_string = arg1_string
                self.arg2_string = arg2_string
                self.modal_is_present = modal_is_present
                self.auxiliary_is_present = auxiliary_is_present
                break


def perform_srl(responses, prompt=None):
    """ Perform semantic role labeling on a list of responses, given a prompt.

    Args:
        responses: a list of responses (or full sentences if prompt = None)
        prompt: the prompt that should be added as a prefix to the responses

    Returns: the output of the AllenNLP SRL model

    """

    predictor = Predictor.from_path(
        "https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
    if prompt:
        sentences = [{"sentence": prompt + " " + response} for response in responses]
    else:
        sentences = [{"sentence": response} for response in responses]
    output = predictor.predict_batch_json(sentences)

    full_output = []
    for sentence, response, srl_results in zip(sentences, responses, output):

        sentence_output = {
            "sentence": sentence["sentence"],
            "prompt": prompt,
            "response": response,
            "srl": srl_results,
        }

        full_output.append(sentence_output)

    return full_output


def identify_argument(verb: Dict, argument_number: int, words: List[str]) -> Tuple[str, List[int]]:
    """
    Identify an argument of a verb on the basis of its number. Returns its string and
    start+end indexes. This allows easier integration of the semantic role labelling
    and coreference results.

    Args:
        verb: the output of AllenNLP's SRL model for this verb
        argument_number: the number of the argument we want to identify
        words: the list of tokens in this sentence

    Returns: a tuple consisting of the argument string and a list of its indexes

    """
    indexes = []
    arg_tokens = []

    tags_words = list(zip(verb["tags"], words))
    for idx, (tag, word) in enumerate(tags_words):
        if tag.endswith(f"ARG{argument_number}"):
            arg_tokens.append(word)
            indexes.append(idx)

    if len(indexes) > 0:
        start_end_indexes = [indexes[0], indexes[-1]]
        arg_string = detokenize(" ".join(arg_tokens))

        return arg_string, start_end_indexes
    else:
        return "-", []

    return "-", []


def find_modal(verb):
    """
    Finds the optional modal verb for a main verb

    Args:
        verb: the SRL output for that verb

    Returns: the string of the modal verb or None

    """
    if "ARGM-MOD" in verb["description"]:
        auxiliary_candidates = re.findall(r"ARGM-MOD: (\w+)", verb["description"])
        if auxiliary_candidates:
            modal = auxiliary_candidates[0]
            modal = VERB_MAP.get(modal, modal)
            return modal

    return None


def get_prompt_from_srl_output(srl_output: Dict) -> str:
    """
    Get the prompt from the SRL output of our perform_srl script.

    Args:
        srl_output: the SRL output of our perform SRL script for a single sentence

    Returns: the prompt of the sentence

    """
    full_sentence = srl_output["sentence"]
    response = srl_output["response"]

    prompt = re.sub(response, "", full_sentence).strip()
    return prompt


def get_number_of_verbs_in_prompt(prompt, srl_output: Dict) -> int:
    """
    Finds the number of verbs in a prompt, given the output of the AllenNLP
    SRL model. This relies on the spaCy tokenizer, which is also used by
    AllenNLP. When there are differences in tokenization, this function may
    give incorrect results

    Args:
        srl_output: the json output of the AllenNLP SRL model

    Returns: the number of verbs in a prompt
    """
    num_verbs = 0
    prompt_tokens = tokenize(prompt)

    for verb in srl_output["srl"]["verbs"]:
        try:
            verb_location = verb["tags"].index("B-V")
        except ValueError:  # if B-V is not in list
            continue

        if verb_location < len(prompt_tokens):
            num_verbs += 1
        else:
            break

    return num_verbs


def process_srl_results(srl_results, num_clusters=10):

    # 2. Get the prompt from the SRL output and determine the number of verbs in the prompt.
    prompt = get_prompt_from_srl_output(srl_results[0])

    sentences = []
    embeddings = sentence_bert_model.encode([s["response"] for s in srl_results])

    # Cluster embeddings
    clusterer = KMeans(n_clusters=num_clusters)
    clusters = clusterer.fit_predict(embeddings)

    # Get similarities to cluster centers
    similarities = []
    for item_idx, cluster in enumerate(clusters):
        cluster_center = clusterer.cluster_centers_[cluster]
        embedding = embeddings[item_idx]
        similarity = 1 - spatial.distance.cosine(embedding, cluster_center)
        similarities.append(similarity)

    # 3. For every sentence:
    for (sent, cluster, similarity) in tqdm(zip(srl_results, clusters, similarities)):

        response = Response(sent, prompt)
        response.parse_sentence()
        response.cluster = cluster
        response.similarity = similarity
        sentences.append(response)

    return sentences


def write_output(all_sentences, output_file):
    """
    Writes tab-separated output that can be imported in a Google Spreadsheet.
    :param all_sentences:
    :param output_file:
    :return:
    """

    with open(output_file, "w") as csvfile:

        csvwriter = csv.writer(csvfile, delimiter="\t")
        csvwriter.writerow(all_sentences[0].tsv_columns())
        for response in all_sentences:
            csvwriter.writerow(response.to_tsv())
