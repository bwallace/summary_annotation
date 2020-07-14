
import random

import json 

import pandas as pd 
import sqlite3


# THIS database will be modified; in practice,
# you'll want to copy the original populated db then 
# run this script.
db_path = "../data/summaries_subset.db"  

def connect_to_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c 

def remove_all_except(cochrane_ids):

    conn, c = connect_to_db()
    
    # drop from generated_summaries and target_summaries
    # tables where the associated Cochrane ID is not
    # in the list
    query = "DELETE FROM generated_summaries WHERE cochrane_id NOT IN ({})".format(", ".join("?" * len(cochrane_ids)))
    c.execute(query, cochrane_ids)

    # now also drop the references
    query = "DELETE FROM target_summaries WHERE cochrane_id NOT IN ({})".format(", ".join("?" * len(cochrane_ids)))
    c.execute(query, cochrane_ids)

    conn.commit()
    conn.close()


def random_sample_cochrane_ids(n, dont_pick=None):
    if dont_pick is None:
        dont_pick = []

    conn, c = connect_to_db()
    excluded_cochrane_ids = []
    query = "SELECT cochrane_id FROM target_summaries"
    all_cochrane_ids = [c_id[0] for c_id in c.execute(query).fetchall()]
    cochrane_ids_with_all_outputs = []

    # exclude cases where we do not have an output for all systems;
    # this can happen specifically for variants that use RoB prioritization
    # because the model may not have returned a score for these, in which
    # case, the system deemed them to be not RCTs.
    # UPDATE this has been resolved, but we still use this to drop
    # studies we wish to explicitly not consider (e.g., that have already 
    # been annotated)
    expected_n_systems = 5
  
    for c_id in all_cochrane_ids:
        q = "SELECT DISTINCT system_id FROM generated_summaries WHERE cochrane_id=?"
        systems = c.execute(q, (c_id,)).fetchall()
        n_unique_systems = len(systems)
        if (n_unique_systems == expected_n_systems) and (c_id not in dont_pick):
            cochrane_ids_with_all_outputs.append(c_id)
        else:
            excluded_cochrane_ids.append(c_id)

    n_excluded = len(set(excluded_cochrane_ids))
    print("excluded {} reviews!".format(n_excluded))
   
    return random.sample(cochrane_ids_with_all_outputs, n)



def make_pilot():
    iain_already_labeled = ['CD000036', 'CD000020', 'CD000025', 'CD000052', 'CD000019', 'CD000088']

    # now add a random set; here we do 18 reviews, which would yield 90 labels to do beyond
    # the 30 for the above (5 systems per) -- totalling 120 labels todo.
    random_set = random_sample_cochrane_ids(18, dont_pick=iain_already_labeled)

    to_keep = iain_already_labeled + random_set

    # TMP
    
    remove_all_except(to_keep)


make_pilot()

