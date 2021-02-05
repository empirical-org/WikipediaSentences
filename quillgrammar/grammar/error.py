from spacy.tokens import Doc


class Error:

    def __init__(self, text: str, index: int, error_type: str,
                 predicted_token: str = None,
                 predicted_sentence: str = None,
                 subject: str = None,
                 subject_idx: int = None,
                 model: str = None,
                 document: Doc = None):

        self.text = text
        self.index = index
        self.type = error_type
        self.predicted_token = predicted_token
        self.predicted_sentence = predicted_sentence
        self.subject = subject
        self.subject_idx = subject_idx
        self.model = model
        self.score = None
        self.document = document

    def __str__(self):
        return "Error(text: {}, index: {}, type: {}, model: {}, score: {})".format(self.text, self.index, self.type, self.model, self.score)

    def __repr__(self):
        return "Error(text: {}, index: {}, type: {}, model: {}, score: {})".format(self.text, self.index, self.type, self.model, self.score)

    def __lt__(self, other):
        return self.score < other.score

    def set_type(self, new_type, config):
        self.type = new_type
        self.score = config["errors"].get(self.type, 0)

    def set_precedence(self, config):
        self.score = config["errors"].get(self.type, 0)
