import requests


def test_preprocessing_api():

    input_file = "data/raw/surge_barriers_but_head.txt"
    url = "http://127.0.0.1:8080/"

    files = {'file': open(input_file, 'rb')}
    values = {'prompt': "A surge barrier in New York City could harm the local ecosystem, but"}

    r = requests.post(url, files=files, data=values)

    assert r.status_code == 200