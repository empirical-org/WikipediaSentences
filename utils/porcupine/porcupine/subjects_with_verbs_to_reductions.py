import json
from collections import Counter
from pattern.en import mood,lemma,tenses
from hashlib import sha256
from .top100 import verbs as top100_verbs
from .literals import verbs as literals_verbs

TEST_DATA='../test/data/sentences.json'

def get_verb_reduction(verb, tag):
    """Given string of existing verb, returns its corresponding reduction
    That's the verb itself if its lemma is in the top100, else its hash"""
    if lemma(verb.lower()) in top100_verbs:
        return verb.upper()
    if lemma(verb.lower()) in literals_verbs:
        return verb.upper()
    else:
        h = sha256(str(tenses(verb)).encode('utf_8')).hexdigest()
        result = tag + '_' + h
        return result


def get_mood(sentence):
    """Returns mood of sentence string"""
    conditional_words = ["assuming", "if", "in case", "no matter how",
            "supposing", "unless", "would", "'d", "should", "could",
            "might", "going to", "whenever", "as long as", "because",
            "in order to"
            ]
    result = mood(sentence)
    if result == 'imperative':
        return 'nonconditional'
    if result in ['subjunctive', 'conditional']:
        for cw in conditional_words:
            if cw in sentence.lower():
                return 'conditional'
        return 'subjunctive'
    return 'nonconditional' # indicative

def get_verb_phrase_reduction(verb_phrase_word_list):
    rl = [get_verb_reduction(vpw['word'], vpw['label']) for vpw in
            verb_phrase_word_list]
    return ':'.join(rl)

def get_noun_phrase_reduction(noun_phrase_word_list):
    npwl = noun_phrase_word_list
    # SG, list len is 1, a singular noun
    if (len(npwl) == 1 and npwl[0]['label'] in
            ['NN', 'NNP']):
        return 'SG'
    # PL, list len is 1, a plural noun
    elif len(npwl) == 1 and npwl[0]['label'] in ['NNS','NNPS']:
        return 'PL'
    # THEYLIKE, list len > 1 and is filled with nouns and pronouns
    elif len(npwl) > 1 and all(npw['label'] in ['PRP','NN','NNP','NNS','NNPS'] for npw in npwl):
        return 'THEY' # TODO: Temporary fix for Porcupine. Should be "THEYLIKE"
    # <determiner literal>, list len is 1, a single determiner
    elif len(npwl) == 1 and npwl[0]['label'] == 'DT':
        return npwl[0]['word'].upper()
    # <pronoun literal>, list len is 1, a single pronoun
    elif len(npwl) == 1 and npwl[0]['label'] == 'PRP':
        return npwl[0]['word'].upper()
    # MOD, list len is 1, a single adjective or adverb
    elif len(npwl) == 1 and npwl[0]['label'] in ['JJ', 'RB']:
        return 'MOD'
    # MODS, list len > 1 and is filled with adverbs and adjectives
    elif len(npwl) > 1 and all(npw['label'] in ['JJ', 'RB'] for npw in npwl):
        return 'MODS'
    # VBG, list len is 1, a single gerund
    elif len(npwl) == 1 and npwl[0]['label'] == 'VBG':
        return 'VBG'
    # INF, list len is >= 2, a single infinitive
    elif (len(npwl) >= 2 and npwl[0]['label'] == 'TO' and
            npwl[1]['label'] == 'VB' and
            all(npw['label'] == 'VBG' for npw in npwl[2:])):
        return 'INF'


def get_reduction(subject_with_verb, sentence):
    result = "{m}-{vp}>{np}"
    m = get_mood(sentence).upper()
    vp = get_verb_phrase_reduction(subject_with_verb['vp'])
    np = get_noun_phrase_reduction(subject_with_verb['np'])
    return result.format(m=m, vp=vp, np=np)


#########################

def test_get_verb_phrase_reduction():
    with open(TEST_DATA) as f:
        test_dict = json.load(f)
    for sentence_obj in test_dict['sentences']:
        expected_reductions = Counter(sentence_obj['reductions']) # order doesn't matter
        subjects_with_verbs = sentence_obj['subjects_with_verbs']
        print (sentence_obj['text'])
        ex, unex = [],[]
        for swv in subjects_with_verbs:
            vpr = get_verb_phrase_reduction(swv['vp'])
            print(vpr)


def test_get_mood():
    with open(TEST_DATA) as f:
        test_dict = json.load(f)
    for sentence_obj in test_dict['sentences']:
        expected_reductions = Counter(sentence_obj['reductions']) # order doesn't matter
        subjects_with_verbs = sentence_obj['subjects_with_verbs']
        sent = sentence_obj['text']
        if sentence_obj['reductions']:
            m = get_mood(sent).upper()
            rm = sentence_obj['reductions'][0].split('-')[0]
        else:
            continue
        if m != rm:
            print(sent)
            print('mood guess, {}, real mood, {}'.format(m, rm))
    return None

def test():
    with open(TEST_DATA) as f:
        test_dict = json.load(f)
    incorrect_sentences = 0
    total_sentences = 0
    for sentence_obj in test_dict['sentences']:
        total_sentences +=1
        expected_reductions = Counter(sentence_obj['reductions']) # order doesn't matter
        subjects_with_verbs = sentence_obj['subjects_with_verbs']
        ex, unex = [],[]
        for swv in subjects_with_verbs:
            r = get_reduction(swv, sentence_obj['text'])
            if r in expected_reductions and expected_reductions[r] > 0:
                ex.append(r)
                expected_reductions[r] -= 1
            else:
                unex.append(r)
        unmatched = [unm for unm in expected_reductions if
                expected_reductions[unm] > 0]

        if unex or unmatched:
            incorrect_sentences +=1
            print('---------------------------------------------')
            print('sentence:')
            print (sentence_obj['text'])
            print('Found {} unexpected and {} unmatched reductions'.format(
                len(unex),
                len(unmatched)))
        if unex:
            print('unexpected:')
            for u in unex:
                print(u)

        if unmatched:
            print('unmatched:')
            for unm in unmatched:
                print(unm)
    print('Out of {} sentences,'.format(total_sentences))
    print('There were {} incorrect sentences.'.format(incorrect_sentences))
    print('{} percent correct.'.format((total_sentences - incorrect_sentences) /
        float(total_sentences) * 100))
    return None

if __name__ == '__main__':
    test()
    #test_get_mood()
    #test_get_verb_phrase_reduction()
