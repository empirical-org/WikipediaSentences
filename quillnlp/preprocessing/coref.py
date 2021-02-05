from quillnlp.utils import detokenize

from allennlp.predictors.predictor import Predictor
import allennlp_models.coref

#coref_predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")
coref_predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2020.02.27.tar.gz")


def get_coreference_dictionary(sentence: str):
    """
    Takes a sentence and returns a dictionary where word indices are mapped to their
    antecedent token.

    Args:
        sentence: the input sentence

    Returns: a dictionary with coreference information, e.g. {"13-13": "Schools"}
    """

    prediction = coref_predictor.predict(document=sentence)

    corefs = {}
    for cluster in prediction["clusters"]:
        antecedent_token_start = cluster[0][0]
        antecedent_token_end = cluster[0][1]
        antecedent_token = prediction["document"][antecedent_token_start: antecedent_token_end + 1]
        for coreferent in cluster[1:]:
            coreferent_token_start = coreferent[0]
            coreferent_token_end = coreferent[1]
            coreferent_token_location = str(coreferent_token_start) + "-" + str(coreferent_token_end)
            corefs[coreferent_token_location] = detokenize(" ".join(antecedent_token))
    return corefs