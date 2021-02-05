from quillnlp.preprocessing.srl import get_number_of_verbs_in_prompt, get_prompt_from_srl_output, identify_argument, \
    find_modal, Response


def test_number_of_verbs_in_prompt1():
    srl_output = {'sentence': 'Governments should make voting compulsory, so community groups and politically motivated action groups should work very hard to inform every otherwise uninformed voter.', 'response': 'community groups and politically motivated action groups should work very hard to inform every otherwise uninformed voter.', 'srl': {'verbs': [{'verb': 'should', 'description': 'Governments [V: should] make voting compulsory , so community groups and politically motivated action groups should work very hard to inform every otherwise uninformed voter .', 'tags': ['O', 'B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'make', 'description': '[ARG0: Governments] [ARGM-MOD: should] [V: make] [ARG1: voting compulsory] , so community groups and politically motivated action groups should work very hard to inform every otherwise uninformed voter .', 'tags': ['B-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'voting', 'description': 'Governments should make [V: voting] compulsory , so community groups and politically motivated action groups should work very hard to inform every otherwise uninformed voter .', 'tags': ['O', 'O', 'O', 'B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'should', 'description': 'Governments should make voting compulsory , so community groups and politically motivated action groups [V: should] work very hard to inform every otherwise uninformed voter .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'work', 'description': 'Governments should make voting compulsory , so [ARG0: community groups and politically motivated action groups] [ARGM-MOD: should] [V: work] [ARGM-MNR: very hard] [ARG1: to inform every otherwise uninformed voter] .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARGM-MNR', 'I-ARGM-MNR', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O']}, {'verb': 'inform', 'description': 'Governments should make voting compulsory , so [ARG0: community groups and politically motivated action groups] should work very hard to [V: inform] [ARG1: every otherwise uninformed voter] .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'O', 'O', 'O', 'O', 'O', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O']}], 'words': ['Governments', 'should', 'make', 'voting', 'compulsory', ',', 'so', 'community', 'groups', 'and', 'politically', 'motivated', 'action', 'groups', 'should', 'work', 'very', 'hard', 'to', 'inform', 'every', 'otherwise', 'uninformed', 'voter', '.']}}
    prompt = get_prompt_from_srl_output(srl_output)
    assert get_number_of_verbs_in_prompt(prompt, srl_output) == 3


def test_number_of_verbs_in_prompt2():
    srl_output = {'sentence': 'Schools should not allow junk food to be sold on campus but a couple options for junk food would be ok.', 'response': 'but a couple options for junk food would be ok.', 'srl': {'verbs': [{'verb': 'should', 'description': 'Schools [V: should] not allow junk food to be sold on campus but a couple options for junk food would be ok .', 'tags': ['O', 'B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'allow', 'description': '[ARG0: Schools] [ARGM-MOD: should] [ARGM-NEG: not] [V: allow] [ARG1: junk food to be sold on campus] but a couple options for junk food would be ok .', 'tags': ['B-ARG0', 'B-ARGM-MOD', 'B-ARGM-NEG', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'be', 'description': 'Schools should not allow junk food to [V: be] sold on campus but a couple options for junk food would be ok .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'sold', 'description': 'Schools should not allow [ARG1: junk food] to be [V: sold] [ARGM-LOC: on campus] but a couple options for junk food would be ok .', 'tags': ['O', 'O', 'O', 'O', 'B-ARG1', 'I-ARG1', 'O', 'O', 'B-V', 'B-ARGM-LOC', 'I-ARGM-LOC', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'would', 'description': 'Schools should not allow junk food to be sold on campus but a couple options for junk food [V: would] be ok .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-V', 'O', 'O', 'O']}, {'verb': 'be', 'description': 'Schools should not allow junk food to be sold on campus but [ARG1: a couple options for junk food] [ARGM-MOD: would] [V: be] [ARG2: ok] .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'B-ARGM-MOD', 'B-V', 'B-ARG2', 'O']}], 'words': ['Schools', 'should', 'not', 'allow', 'junk', 'food', 'to', 'be', 'sold', 'on', 'campus', 'but', 'a', 'couple', 'options', 'for', 'junk', 'food', 'would', 'be', 'ok', '.']}}
    prompt = get_prompt_from_srl_output(srl_output)
    assert get_number_of_verbs_in_prompt(prompt, srl_output) == 4


def test_would():
    srl_output = {'sentence': 'A surge barrier in New York City could harm the local ecosystem, but it would save billions of dollars and many human lives.', 'prompt': 'A surge barrier in New York City could harm the local ecosystem, but', 'response': 'it would save billions of dollars and many human lives.', 'srl': {'verbs': [{'verb': 'harm', 'description': '[ARG0: A surge barrier in New York City] [ARGM-MOD: could] [V: harm] [ARG1: the local ecosystem] , but it would save billions of dollars and many human lives .', 'tags': ['B-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'save', 'description': 'A surge barrier in New York City could harm the local ecosystem , but [ARG0: it] [ARGM-MOD: would] [V: save] [ARG1: billions of dollars and many human lives] .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O']}], 'words': ['A', 'surge', 'barrier', 'in', 'New', 'York', 'City', 'could', 'harm', 'the', 'local', 'ecosystem', ',', 'but', 'it', 'would', 'save', 'billions', 'of', 'dollars', 'and', 'many', 'human', 'lives', '.']}}
    arg0_string, arg0_indices = identify_argument(srl_output["srl"]["verbs"][1], 0, srl_output["srl"]["words"])
    arg1_string, arg1_indices = identify_argument(srl_output["srl"]["verbs"][1], 1, srl_output["srl"]["words"])

    assert arg0_string == "it"
    assert arg0_indices == [14, 14]

    assert arg1_string == "billions of dollars and many human lives"
    assert arg1_indices == [17, 23]

    modal = find_modal(srl_output["srl"]["verbs"][1])
    assert modal == "would"


def test_parsing1():
    srl_output = {'sentence': 'A surge barrier in New York City could harm the local ecosystem, but it would save billions of dollars and many human lives.', 'prompt': 'A surge barrier in New York City could harm the local ecosystem, but', 'response': 'it would save billions of dollars and many human lives.', 'srl': {'verbs': [{'verb': 'harm', 'description': '[ARG0: A surge barrier in New York City] [ARGM-MOD: could] [V: harm] [ARG1: the local ecosystem] , but it would save billions of dollars and many human lives .', 'tags': ['B-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'save', 'description': 'A surge barrier in New York City could harm the local ecosystem , but [ARG0: it] [ARGM-MOD: would] [V: save] [ARG1: billions of dollars and many human lives] .', 'tags': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O']}], 'words': ['A', 'surge', 'barrier', 'in', 'New', 'York', 'City', 'could', 'harm', 'the', 'local', 'ecosystem', ',', 'but', 'it', 'would', 'save', 'billions', 'of', 'dollars', 'and', 'many', 'human', 'lives', '.']}}

    response = Response(srl_output,
                        "A surge barrier in New York City could harm the local ecosystem, but")

    assert response.profanity == ""
    assert response.too_short is False
    assert response.too_long is False

    response.parse_sentence()

    assert response.verb_string == "save (would)"
    assert response.arg1_string == "billions of dollars and many human lives"


def test_parsing2():
    srl_output = {'sentence': 'A surge barrier in New York City could harm the local ecosystem, but could prevent billions of dollars worth of damage to the city.', 'prompt': 'A surge barrier in New York City could harm the local ecosystem, but', 'response': 'could prevent billions of dollars worth of damage to the city.', 'srl': {'verbs': [{'verb': 'harm', 'description': '[ARG0: A surge barrier in New York City] [ARGM-MOD: could] [V: harm] [ARG1: the local ecosystem] , but could prevent billions of dollars worth of damage to the city .', 'tags': ['B-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'prevent', 'description': '[ARG0: A surge barrier in New York City] could harm the local ecosystem , but [ARGM-MOD: could] [V: prevent] [ARG1: billions of dollars worth of damage to the city] .', 'tags': ['B-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'I-ARG0', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O']}], 'words': ['A', 'surge', 'barrier', 'in', 'New', 'York', 'City', 'could', 'harm', 'the', 'local', 'ecosystem', ',', 'but', 'could', 'prevent', 'billions', 'of', 'dollars', 'worth', 'of', 'damage', 'to', 'the', 'city', '.']}}
    response = Response(srl_output,
                        "A surge barrier in New York City could harm the local ecosystem, but")

    response.parse_sentence()

    assert response.verb_string == "prevent (could)"

