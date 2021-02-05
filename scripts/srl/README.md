## Data preprocessing

Our preprocessing script combines semantic role labeling with coreference resolution, semantic clustering 
and a range of other checks to preprocess Comprehension data for labeling.

Semantic role labelling identifies the verbs in a sentence and the semantic roles that are associated with them.
These roles are:

- arg0: the 'agent': the entity that initiates an action
- arg1: the 'patient': the entity that undergoes an action or undergoes a change of state
- arg2: the 'beneficiary': the entity for whose benefit the action was performed

### Script

`preprocess.py` takes 3 arguments:

- the input file with responses (txt format, 1 response per line)
- the output file where the raw AllenNLP output should be saved (json format)
- an optional prompt (which will be added to the responses to have a full sentence)

It reads the input file and applies SRL to every line:

1. If a prompt is provided, it is added to every sentence.
2. The AllenNLP SRL model is applied to all sentences.
3. The results are saved as a list of json objects in a json file. Every json object has three fields:
"sentence" contains the original sentence, "response" contains the response part of the sentence
(without the prompt), and "srl" contains the raw AllenNLP output.

Then it takes the following preprocessing steps:

2. Get the prompt from the SRL output and determine the number of verbs in the prompt.
We do this because the verbs in the prompt do not interest us: they are the same for all
responses.
3. For every sentence:

    3.1 Perform a number of checks, like the opinion check and a check for sentences that are too long or too short.

    3.2 Perform coreference resolution on the full sentence. The result is a coreference
    dictionary that maps every word in a coreference chain (such as "they") to its
    antecedent (such as "students").

    3.3 For each of the verbs in the sentence, preprocess the verb and identify its arguments.

        3.2.1 Preprocess the verb (tokenized by AllenNLP) using a few simple rules, e.g. ca => can, etc.

        3.2.2 If the verb is an auxiliary, add this information to the metadata and
        add the verb as an auxiliary to the next main verb.

        3.2.3 If the verb is not a modal or auxiliary, identify the arguments in the sentence.
        If arg0 is in the coreference dictionary, identify its antecedent (the "implied subject").
        If not, take the arg0 itself as "implied subject".

        3.2.4 Add the verb information to the sentence information.
        Exclude constructions like "I think", "I guess", etc. on the basis of a
        list of subjects we want to ignore (e.g. "I", "some", "some people")


Also see the more conceptual documentation on the following Notion page:
https://www.notion.so/quill/System-Map-Parsing-Quill-Comprehension-Sentences-98170606ffcb4b2ba4af9a1664b5beae