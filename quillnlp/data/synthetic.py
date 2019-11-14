from typing import List, Dict
from google.cloud import translate

# Instantiates a client
translate_client = translate.Client()


def generate_synthetic_data(items: List[Dict], lang: str) -> List[Dict]:
    """
    Generates a list of synthetic data from a list of items by back-translating the
    text of the items to the specified language and back to English. Back-translation
    will be done with Google Translate. To connect with Google Translate, the environment
    variable GOOGLE_APPLICATION_CREDENTIALS needs to refer to the key file.

    Args:
        items: the list of items whose "text" field will be backtranslated
        lang: the language through which backtranslation will be performed

    Returns: a list of backtranslated items

    """

    translated_items = []
    for item in items:

        translation = translate_client.translate(item["text"], target_language=lang)
        back_translation = translate_client.translate(translation["translatedText"],
                                                      target_language="en")

        translated_items.append({"source_text": item["text"],
                                 "text": back_translation["translatedText"],
                                 "label": item["label"]})

    return translated_items
