# -*- coding: utf-8 -*-
from flask import request, \
     render_template, flash, Flask
from flask import jsonify
from pathlib import Path
print('Loading subject-verb agreement models...')
#from sva_classifier import get_feedback
from qcorrector import check as get_feedback
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from sqlalchemy.ext.declarative import declarative_base


# DB CONFIG AND SETUP ##################################################################

DB_PASS = os.environ['PORCUPINE_DB_PASS']
Base = declarative_base()
engine = \
        create_engine('postgres://porcupine:{}@localhost:5432/porcupine'.format(DB_PASS))
Session = sessionmaker(bind=engine)
session = Session()


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    correct = Column(Boolean)
    primary_error = Column(String)
    specific_error = Column(String)

    def __repr__(self):
        return "<Submission {}...>".format(self.text[:30])


try:
    Base.metadata.create_all(engine)
except:
    pass # it already exists

# ROUTES AND APP ##########################################################################

app = Flask(__name__)
app.secret_key = 'dddxasdasd' # needed for message flashing

@app.route('/submissions', methods=['GET'])
def list_submissions():
    """List the past submissions with information about them"""
    submissions = []
    try:
        submissions = session.query(Submission).all()
    except SQLAlchemyError as e:
        session.rollback()
    return render_template('list_submissions.html', submissions=submissions)

@app.route('/submissions.json', methods=['GET'])
def get_submissions():
    """API endpoint to get submissions in JSON format"""
    print(request.args.to_dict())
    print(request.args.get('search[value]'))
    print(request.args.get('draw', 1))
    # submissions  = session.query(Submission).all()
    if request.args.get('correct_filter', 'all') == 'all':
        correct_filter = [True, False]
    elif request.args['correct_filter'] == 'correct':
        correct_filter = [True]
    else:
        correct_filter = [False]

    if request.args.get('order[0][column]', '0') == '0':
        column = 'id'
    elif request.args['order[0][column]'] == '1':
        column = 'text'
    else:
        column = 'primary_error'

    order_str = "{} {}".format(column, request.args.get('order[0][dir]', 'desc'))

    search_val = request.args.get('search[value]')
    draw = request.args.get('draw', 1)
    filtered_len = session.query(Submission)\
            .filter(Submission.text.startswith(search_val))\
            .filter(Submission.correct.in_(correct_filter))\
            .count()
    subs = \
            session.query(Submission).filter(Submission.text.startswith(search_val))\
            .filter(Submission.correct.in_(correct_filter))\
            .order_by(order_str)\
            .offset(request.args.get('start', 0))\
            .limit(request.args.get('length', 10))\
            .all()
    submissions = {'draw': draw, 'recordsTotal':0, 'recordsFiltered':0, 'data':[]}
    i = 0
    for i, submission in enumerate(subs):
       submissions['data'].append([submission.id, submission.text,
           submission.primary_error, submission.correct])
    submissions['recordsTotal'] = session.query(Submission).count()
    submissions['recordsFiltered'] = filtered_len

    return jsonify(submissions)


@app.route('/', methods=['GET', 'POST'])
def check_sentence():
    """Sole porcupine endpoint"""
    text = ''
    if request.method == 'POST':
        text = request.form['text']
        if not text:
            error = 'No input'
            flash_message = error
        else:
            fb = get_feedback(request.form['text'])
            correct = request.form.get('is_correct') or not fb.primary_error
            sub = Submission(text=text, correct=correct, primary_error=fb.primary_error,
                    specific_error=fb.specific_error)
            session.add(sub)
            session.commit()
            # TODO: remove the hack below
            if not fb.primary_error:
                fb.human_readable = "No errors were found."
            flash_message = fb.human_readable

        flash(flash_message)
    return render_template('check_sentence.html', text=text)

if __name__ == '__main__':
    app.run(port=10400, host= '0.0.0.0', debug=False)
