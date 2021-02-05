import random

from collections import defaultdict, Counter

from quillnlp.grammar.myspacy import nlp


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])


def sample_ngrams(model, texts, prompt=""):
    """
    Sample random ngrams from a list of texts

    Args:
        model: a SpaCy model
        texts (list): a list of texts

    Returns:
        A list with n-grams of length 1 to 5 sampled from the texts.
    """
    ngrams = []
    for text in texts:
        if random.random() < 0.25:
            doc = model(text)

            tokens = [t.orth_ for t in doc if t.idx >= len(prompt)]
            ngram_length = random.randint(1, 5)
            all_ngrams = [" ".join(x) for x in find_ngrams(tokens, ngram_length)]
            if len(all_ngrams) > 0:
                ngrams.append(random.choice(list(all_ngrams)).strip())

    return ngrams


def random_mask(model, texts, token_probs, max_seq_len, prob=0.1, prompt=""):
    """
    Args:
        model: a SpaCy model.
        texts (list): a list of texts
        token_probs (dict): a dictionary with word probabilities
        prob (float): a masking/replacement probability

    Returns:
        A list where prob% of the tokens in the texts have been masked and another prob%
        have been replaced by a token with the same part of speech.
    """
    synthetic_texts = []

    for txt in texts:
        doc = model(txt)
        new_tokens = []

        for tok in doc:

            # Do not replace tokens in the prompt
            if tok.idx < len(prompt):
                new_tokens.append(tok.text_with_ws)
                continue

            # Do not replace punctuation signs.
            elif tok.pos_ == "PUNCT":
                new_tokens.append(tok.text_with_ws)
                continue

            # Sample a random score
            score = random.random()

            #  If the score is lower than 0.1, we mask the token
            if score < prob:
                new_tokens.append("[MASK]" + tok.whitespace_)

            #  If the score is lower than 0.2 but higher than 0.1,
            #  we replace the token by a token with the same part-of-speech.
            elif score < prob * 2:
                target = random.choices(token_probs[tok.pos_]["tokens"], token_probs[tok.pos_]["probs"])
                new_tokens.append(target[0].orth_ + tok.whitespace_)
            else:
                new_tokens.append(tok.text_with_ws)

        if len(new_tokens) < max_seq_len:
            masked_doc = "".join(new_tokens)
            synthetic_texts.append(masked_doc.strip())

    return synthetic_texts


def compute_pos_stats(model, texts):
    """
    Computes part of speech statistics from a list of texts.

    Args:
        model: a spaCy model
        texts (list): a list of texts

    Returns:
        A dictionary that maps from parts of speech to a dictionary that maps words to
        their probabilities given the part of speech.
        Example: {"NOUN": {"table": 0.2, "coffee": 0.8}}
    """

    pos2tokens = defaultdict(Counter)

    for txt in texts:
        doc = model(txt)
        for token in doc:
            pos2tokens[token.pos_].update([token])

    for pos in pos2tokens:
        tot_sum = sum(pos2tokens[pos].values())

        for word in pos2tokens[pos]:
            pos2tokens[pos][word] /= tot_sum

    dict_pos = {}
    for pos in pos2tokens:
        for token, prob in pos2tokens[pos].items():
            if pos not in dict_pos:
                dict_pos[pos] = {"tokens": [], "probs": []}
            dict_pos[pos]["tokens"].append(token)
            dict_pos[pos]["probs"].append(prob)

    return dict_pos


def augment_data(texts, prompt="", n_iter=5):
    """
    Create synthetic training data from an original set of training data.

    Args:
        lang_data (str): the prefix of a language (for now, "fr", "it", "de" or "es").
        n_iter:          The umber of iterations of selected

    Returns: The list containing the augmented review
    """

    pos2tokens = compute_pos_stats(nlp, texts)

    synthetic_texts = set()
    for i in range(n_iter):
        print(f"Iteration {i}: masking")
        synthetic_texts.update([i for i in random_mask(nlp, texts, pos2tokens, 512, prompt=prompt)])

        print(f"Iteration {i}: n-gram sampling")
        synthetic_texts.update(sample_ngrams(nlp, texts, prompt))

    return synthetic_texts