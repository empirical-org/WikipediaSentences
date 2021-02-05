import os

from flask import Flask, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename

from quillnlp.preprocessing.srl import process_srl_results, perform_srl, write_output


UPLOAD_FOLDER = "/tmp/"

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        return "This is Quill's preprocessing engine"
    else:

        prompt = request.form['prompt']
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.rsplit('.', 1)[1].lower() == "txt":
            filename = secure_filename(file.filename)
            full_filename = os.path.join(UPLOAD_FOLDER, filename)
            file.save(full_filename)

            # 1. Perform SRL
            print("Performing SRL...")
            with open(full_filename) as i:
                responses = [line.strip() for line in i]

            srl_results = perform_srl(responses, prompt)

            # 2. Postprocess SRL
            print("Postprocessing SRL...")
            sentences = process_srl_results(srl_results)

            output_tsv_file = full_filename.replace(".txt", ".tsv")
            write_output(sentences, output_tsv_file)
            return send_file(output_tsv_file)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080)
