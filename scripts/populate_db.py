
import pandas as pd 

import sqlite3

db_path = "../data/summaries.db"  


def connect_to_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c 

def add_references(reference_summary_path="../data/output_abs_title.csv"):   
    conn, c = connect_to_db()

    # NOTE that in fact any system output file will do here, since all
    # contain the targets -- here we ignore system specific output
    references_df = pd.read_csv(reference_summary_path)

    for i, reference_summary in references_df.iterrows():

        target = reference_summary["Clean_Summary"]
        title = ""
        c.execute("""INSERT INTO target_summaries (uuid, cochrane_id, title, summary) VALUES (?, ?, ?, ?)""",
                                                        (i, reference_summary['Cochrane ID'], 
                                                        title, target))

    conn.commit()
    conn.close()


def add_sources(sources_path="../data/sources.csv"):
    conn, c = connect_to_db()

    sources_df = pd.read_csv(sources_path)
    failures = 0 

    for i, review_sources in sources_df.iterrows():
        # forgive me.
        titles = eval(review_sources["Title"])

        def sad_hack(maybe_a_str_list):
            # this is neccessary because some of the sets of abstracts
            # are malformed -- seemingly ending midsentence... 
            # TODO this needs to be fixed.
            if not maybe_a_str_list.endswith("']"):
                return maybe_a_str_list + "']"
            return maybe_a_str_list

        try:
            abstracts = eval(sad_hack(review_sources["Abstract"]))

            # TODO this column name should be fixed.
            cochrane_id = review_sources["Unnamed: 0"] 
            
            for title, abstract in zip(titles, abstracts):

                c.execute("""INSERT INTO source_abstract (cochrane_id, title, abstract) VALUES (?, ?, ?)""",
                                                                (cochrane_id, title, abstract)) 
        except:
            print("failed to add a source!", i)
            failures += 1

    print("{} failures.".format(failures))
    conn.commit()
    conn.close()                                              


def add_system_outputs(sys_id, data_path):
    conn, c = connect_to_db()

    system_df = pd.read_csv(data_path)
    for i, generated_summary in system_df.iterrows():
        generated = generated_summary['Prediction_Summary']
        c.execute("""INSERT INTO generated_summaries (uuid, cochrane_id, system_id, summary) VALUES (?, ?, ?, ?)""",
                                                        (i, generated_summary['Cochrane ID'], 
                                                        sys_id, generated))

    conn.commit()
    conn.close()


add_references()
add_system_outputs("BART-none-abs-title", "../data/output_abs_title.csv")
add_sources()



