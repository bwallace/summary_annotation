from typing import Dict, Tuple, Sequence

from flask import Flask, jsonify, request, render_template, url_for, redirect
import json 
import sqlite3

app = Flask(__name__)

db_path = "data/summaries.db"  


@app.route('/')
def hello():
    return next()



def get_summaries_for_uid(cochrane_id) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    
    with sqlite3.connect(db_path) as con:
        reference_summary, title = con.execute("""SELECT summary, title FROM target_summaries where cochrane_id='{}';""".format(cochrane_id)).fetchone()
        
        rows = con.execute("""SELECT uuid, summary, system_id FROM generated_summaries where cochrane_id='{}';""".format(cochrane_id)).fetchall()
        
        uuids = []
        pred_summaries = []
        systems = []
        for row in rows:
            u_id, pred_summ, system =  row[0], row[1], row[2]
            uuids.append(u_id)
            pred_summaries.append(pred_summ)
            systems.append(system)
        # now get the reference summary
        
        return (reference_summary, title, systems, pred_summaries, uuids)


'''def get_summaries_for_uid(uid) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    
    with sqlite3.connect(db_path) as con:
        cochrane_id, pred_summary, system = con.execute("""SELECT cochrane_id, summary, system_id FROM generated_summaries where uuid='{}';""".format(uid)).fetchone()
        # now get the reference summary
        reference_summary, title = con.execute("""SELECT summary, title FROM target_summaries where cochrane_id='{}';""".format(cochrane_id)).fetchone()
        
        return (reference_summary, title, system, pred_summary)'''


@app.route('/view_sources/<uid>')
def view_sources(uid):
    with sqlite3.connect(db_path) as con:
        cochrane_id = con.execute("""SELECT cochrane_id FROM generated_summaries where uuid='{}';""".format(uid)).fetchone()[0]
        sources = con.execute("""SELECT title, abstract FROM source_abstract WHERE cochrane_id='{}';""".format(cochrane_id)).fetchall()
        return render_template('show_sources.html', source_abstracts=sources)

def get_n_labels():
    with sqlite3.connect(db_path) as con:
        q_str = """SELECT count(*) FROM label WHERE 1"""
        return con.execute(q_str).fetchone()[0]

@app.route('/annotate/<uid>')
def annotate(uid):
    # uid is a unique identifier for a *generated*
    # summary. 
    reference, review_title, systems, predictions, uuids = get_summaries_for_uid(uid)

    # this is terrible but right now we collect 3 annotations per doc, so... yeah
    n_labels_per_doc = 16
    n_done = str(int(get_n_labels()/n_labels_per_doc))

    return render_template('annotate.html', uid=uuids, review_title=review_title, 
                            reference=reference, prediction=predictions, system=systems,
                            already_done=n_done)


def next():
    ''' pick a rando prediction in the system that hasn't been annotated, display it. '''
    with sqlite3.connect(db_path) as con:
        # NOTE this is inefficient, but who cares for our case
        q_str = """SELECT uuid FROM generated_summaries WHERE NOT EXISTS (
                    SELECT * FROM label WHERE generated_summaries.uuid = label.generated_summary_id) 
                    ORDER BY COCHRANE_ID, RANDOM() LIMIT 1;"""


        next_uuid = con.execute(q_str).fetchone()
        coch_id = con.execute("""SELECT cochrane_id FROM generated_summaries where uuid='{}';""".format(next_uuid[0])).fetchone()
        print(coch_id)
        if next_uuid is None:
            return render_template("all_done.html")
        return annotate(coch_id[0])




@app.route('/save_annotation/<uid>', methods = ['POST'])
def save_annotation(uid):
    uid = eval(uid)
    relevancy_score1  = int(request.form['likert_relevance1'])
    relevancy_score2  = int(request.form['likert_relevance2'])
    relevancy_score3  = int(request.form['likert_relevance3'])
    relevancy_score4  = int(request.form['likert_relevance4'])

    factuality_score1 = int(request.form['likert_facts1'])
    factuality_score2 = int(request.form['likert_facts2'])
    factuality_score3 = int(request.form['likert_facts3'])
    factuality_score4 = int(request.form['likert_facts4'])

    fluency_score1    = int(request.form['likert_fluency1'])
    fluency_score2    = int(request.form['likert_fluency2'])
    fluency_score3    = int(request.form['likert_fluency3'])
    fluency_score4    = int(request.form['likert_fluency4'])

    direction_score1    = int(request.form['likert_direction1'])
    direction_score2    = int(request.form['likert_direction2'])
    direction_score3    = int(request.form['likert_direction3'])
    direction_score4    = int(request.form['likert_direction4'])
    review_title = str(request.form['review_title'])
    print(review_title)

    with sqlite3.connect(db_path) as con:
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[0], "factuality", factuality_score1))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[1], "factuality", factuality_score2))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[2], "factuality", factuality_score3))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[3], "factuality", factuality_score4))

        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[0], "fluency", fluency_score1))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[1], "fluency", fluency_score2))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[2], "fluency", fluency_score3))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[3], "fluency", fluency_score4))


        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[0], "relevance", relevancy_score1))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[1], "relevance", relevancy_score2))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[2], "relevance", relevancy_score3))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[3], "relevance", relevancy_score4))


        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[0], "direction", direction_score1))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[1], "direction", direction_score2))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[2], "direction", direction_score3))
        con.execute("""INSERT INTO label (generated_summary_id, label_type, score) VALUES (?, ?, ?);""",
                                                        (uid[3], "direction", direction_score4))

        con.commit()

    #return next()
    return redirect(url_for('hello'))
