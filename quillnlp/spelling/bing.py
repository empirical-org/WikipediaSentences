import requests

from private import BING_URL, BING_KEY


def correct_sentence_with_bing(sentence: str) -> str:
    data = {'text': sentence}

    params = {
        'mkt': 'en-us',
        'mode': 'proof'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': BING_KEY,
    }

    response = requests.post(BING_URL, headers=headers, params=params, data=data).json()
    print(response)

    corrections = []
    for error in response["flaggedTokens"]:
        if len(error["suggestions"]) > 0:
            corrections.append((error["offset"], error["token"], error["suggestions"][0]["suggestion"]))

    corrections.sort(reverse=True)

    for offset, token, replacement in corrections:
        sentence = sentence[:offset] + replacement + sentence[offset+len(token):]

    return sentence