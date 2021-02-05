from quillnlp.grammar.myspacy import nlp
from quillnlp.grammar.verbutils import get_subject

def test_subjects():

    sentences = [("There is fireworks going off in the night sky right now",
                  1, "fireworks"),
                 ("Standing beside me are my best friend.",
                  3, "my best friend"),
                 ("Experts have argued that it exacerbate depression and weakens the immune system.",
                  8, "it"),
                 ("Through the tunnel is a giant city, which some people call the Capitol.",
                  3, "a giant city"),
                 ("Some people like Taylor Swift, but others love Taylor Swift.",
                  8, "others"),
                 ("Studying in the library is my classmate, and she is probably preparing for the same test that I am.",
                  4, "my classmate")]

    for sentence, index, subject in sentences:
        doc = nlp(sentence)

        print([(x, x.dep_, list(x.lefts), list(x.rights), x.left_edge, x.head) for x in doc])

        predicted_subject = get_subject(doc[index], full=True)
        if predicted_subject is not None:
            predicted_subject = "".join([t.text_with_ws for t in predicted_subject]).strip()

        assert predicted_subject == subject
