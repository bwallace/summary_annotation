from typing import Dict, Tuple, Sequence

from flask import Flask, jsonify, request, render_template
import json 
import sqlite3

app = Flask(__name__)

db_path = "data/summaries.db"  


@app.route('/')
def hello():
    return next()

def get_summaries_for_uid(uid) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    
    with sqlite3.connect(db_path) as con:
        cochrane_id, pred_summary, system = con.execute("""SELECT cochrane_id, summary, system_id FROM generated_summaries where uuid='{}';""".format(uid)).fetchone()
        # now get the reference summary
        reference_summary, title = con.execute("""SELECT summary, title FROM target_summaries where cochrane_id='{}';""".format(cochrane_id)).fetchone()
        
        return (reference_summary, title, system, pred_summary)


@app.route('/view_sources/<uid>')
def view_sources(uid):
    with sqlite3.connect(db_path) as con:
        cochrane_id = con.execute("""SELECT cochrane_id FROM generated_summaries where uuid='{}';""".format(uid)).fetchone()[0]
        sources = con.execute("""SELECT title, abstract FROM source_abstract WHERE cochrane_id='{}';""".format(cochrane_id)).fetchall()
        return render_template('show_sources.html', source_abstracts=sources)

@app.route('/annotate/<uid>')
def annotate(uid):
    # uid is a unique identifier for a *generated*
    # summary. 
    reference, review_title, system, prediction = get_summaries_for_uid(uid)
    return render_template('annotate.html', uid=uid, review_title=review_title, 
                            reference=reference, prediction=prediction, system=system)


def next():
    ''' pick a rando prediction in the system that hasn't been annotated, display it. '''
    with sqlite3.connect(db_path) as con:
        # NOTE this is inefficient, but who cares for our case
        q_str = """SELECT uuid FROM generated_summaries WHERE NOT EXISTS (
                    SELECT * FROM label WHERE generated_summaries.uuid = label.generated_summary_id) 
                    ORDER BY COCHRANE_ID, RANDOM() LIMIT 1;"""
        next_uuid = con.execute(q_str).fetchone()[0]
        return annotate(next_uuid)



@app.route('/save_annotation/<uid>', methods = ['POST'])
def save_annotation(uid):
    
    factuality_score = int(request.form['likert_facts'])
    fluency_score    = int(request.form['likert_fluency'])

    with sqlite3.connect(db_path) as con:
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid, "factuality", factuality_score))

        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid, "fluency", fluency_score))
        con.commit()

    return next()
