from typing import Dict, Tuple, Sequence

from flask import Flask, jsonify, request, render_template, url_for, redirect
import json 
import sqlite3
from random import shuffle
app = Flask(__name__)
import math
db_path = "data/summaries.db"  


@app.route('/')
def hello():
    return next()


n_labels_per_doc = 4
n_docs = 5
def get_n_labels():
    with sqlite3.connect(db_path) as con:
        q_str = """SELECT count(*) FROM label """
        return con.execute(q_str).fetchone()[0]

def get_summaries_for_uid(cochrane_id) -> Tuple[str]:
    # return (target, title, predicted) summary for this *prediction* uid.
    
    with sqlite3.connect(db_path) as con:
        reference_summary, title = con.execute("""SELECT summary, title FROM target_summaries where cochrane_id='{}';""".format(cochrane_id)).fetchone()
        
        #get all summaries with the cochrane id 
        rows = con.execute("""SELECT uuid, summary, system_id FROM generated_summaries where cochrane_id='{}';""".format(cochrane_id)).fetchall()
        
        ##shuffle them 
        shuffle(rows)
        
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


@app.route('/annotate/<uid>')
def annotate(uid):
    # uid is a unique identifier for a *generated*
    # summary. 
    reference, review_title, systems, predictions, uuids = get_summaries_for_uid(uid)

    # this is terrible but right now we collect 3 annotations per doc, so... yeah
    print(get_n_labels())
    n_done = str(math.floor(int(get_n_labels()/(n_labels_per_doc * n_docs))))

    return render_template('annotate_relevancy_fluency.html', idx = 0, uuids=uuids, review_title=review_title, 
                            reference=reference, predictions=predictions, systems=systems,
                            already_done=n_done)


def next():
    ''' pick a rando prediction in the system that hasn't been annotated, display it. '''
    with sqlite3.connect(db_path) as con:
        

        q_str = """SELECT uuid FROM generated_summaries WHERE NOT {} = (
                    SELECT COUNT(*) FROM label WHERE generated_summaries.uuid = label.generated_summary_id) 
                    ORDER BY COCHRANE_ID, RANDOM() LIMIT 1;""".format(4)


        next_uuid = con.execute(q_str).fetchone()

        if next_uuid is None:
            return render_template("all_done.html")

        # get the cochrane id of the randomly selected unannotated summary
        coch_id = con.execute("""SELECT cochrane_id FROM generated_summaries where uuid='{}';""".format(next_uuid[0])).fetchone()
        print(coch_id)
        
        return annotate(coch_id[0])

def insert_label(con, uid, label_type, score):
    check_exist_str = "SELECT uuid from label where generated_summary_id = '{}' AND label_type ='{}'""".format(uid, label_type)
    label_uuid = con.execute(check_exist_str).fetchone()
    if label_uuid != None:
        label_uuid = label_uuid[0]

    con.execute("""INSERT OR REPLACE INTO label (uuid, generated_summary_id, label_type, score) VALUES (?, ?, ?, ?);""",
                                                                (label_uuid, uid, label_type, score))
    con.commit()

@app.route('/save_factuality_annotation/<uuids>', methods = ['POST'])
def save_factuality_annotation(uuids):
    uuids = eval(uuids)
    button_val = str(request.form['button'])


    review_title = str(request.form['review_title'])
    reference = str(request.form['reference'])
    predictions = eval(request.form['predictions'])
    systems = eval(request.form['systems'])

    print(predictions)

    if button_val == 'submit':
        with sqlite3.connect(db_path) as con:

            for idx, uid in enumerate(uuids):
            
                system = systems[idx]
                request_key = 'likert_facts%s'%(str(idx + 1))
                factuality_score    = int(request.form[request_key])
                insert_label(con, uid, "%s-factuality"%(system), factuality_score)

    
    n_done = str(math.floor(int(get_n_labels()/(n_labels_per_doc * n_docs))))

    if button_val == 'back':
        return render_template('annotate_direction.html', uuids=uuids, review_title=review_title, 
                                reference=reference, predictions=predictions, systems=systems,
                                already_done=n_done)

    if button_val == 'clear':
        return render_template('annotate_factuality.html', uuids=uuids, review_title=review_title, 
                                reference=reference, predictions=predictions, systems=systems,
                                already_done=n_done)

    return redirect(url_for('hello'))



@app.route('/save_direction_annotation/<uuids>', methods = ['POST'])
def save_direction_annotation(uuids):
    uuids = eval(uuids)
    button_val = str(request.form['button'])

    
    review_title = str(request.form['review_title'])
    reference = str(request.form['reference'])
    predictions = eval(request.form['predictions'])
    systems = eval(request.form['systems'])

    print(predictions)

    if button_val == 'submit':
        with sqlite3.connect(db_path) as con:

            for idx, uid in enumerate(uuids):
            
                system = systems[idx]
                request_key = 'likert_direction%s'%(str(idx + 1))
                direction_score    = int(request.form[request_key])
                insert_label(con, uid, "%s-direction"%(system), direction_score)

    n_done = str(math.floor(int(get_n_labels()/(n_labels_per_doc * n_docs))))

    if button_val == 'back':
        
        return render_template('annotate_relevancy_fluency.html', idx = len(uuids) -1, uuids=uuids, review_title=review_title, 
                            reference=reference, predictions=predictions, systems=systems,
                            already_done=n_done)

    elif button_val == 'clear':
        return render_template('annotate_direction.html', uuids=uuids, review_title=review_title, 
                                reference=reference, predictions=predictions, systems=systems,
                                already_done=n_done)

    return render_template('annotate_factuality.html', uuids=uuids, review_title=review_title, 
                                reference=reference, predictions=predictions, systems=systems,
                                already_done=n_done)

    
    

                     
@app.route('/save_annotation/<uuids>', methods = ['POST'])
def save_annotation(uuids):
    uuids = eval(uuids)
    button_val = str(request.form['button'])
    
    idx = int(request.form['idx'])
    review_title = str(request.form['review_title'])
    reference = str(request.form['reference'])
    predictions = eval(request.form['predictions'])
    print(predictions)
    systems = eval(request.form['systems'])

    prev_idx = idx - 1
    next_idx = idx + 1
    

    print(review_title, idx)

    if button_val == 'submit':
        with sqlite3.connect(db_path) as con:
            uid = uuids[idx]
            system = systems[idx]
            relevancy_score  = int(request.form['likert_relevance'])
            fluency_score    = int(request.form['likert_fluency'])

            insert_label(con, uid, "%s-relevance"%(system), relevancy_score)
            insert_label(con, uid, "%s-fluency"%(system), fluency_score)
            
    
    
    n_done = str(math.floor(int(get_n_labels()/(n_labels_per_doc * n_docs))))

    if button_val == 'submit' and next_idx < len(uuids):

            return render_template('annotate_relevancy_fluency.html', idx = next_idx, uuids=uuids, review_title=review_title, 
                                reference=reference, predictions=predictions, systems=systems,
                                already_done=n_done)
    
    elif button_val == 'clear':
        return render_template('annotate_relevancy_fluency.html', idx = idx, uuids=uuids, review_title=review_title, 
                            reference=reference, predictions=predictions, systems=systems,
                            already_done=n_done)

    elif button_val == 'back':
        
        return render_template('annotate_relevancy_fluency.html', idx = prev_idx, uuids=uuids, review_title=review_title, 
                            reference=reference, predictions=predictions, systems=systems,
                            already_done=n_done)

    

    return render_template('annotate_direction.html', uuids=uuids, review_title=review_title, 
                                reference=reference, predictions=predictions, systems=systems,
                                already_done=n_done)
