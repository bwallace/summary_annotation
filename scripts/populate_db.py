
import math 

import pandas as pd 

import sqlite3

db_path = "../data/summaries.db"  
cochrane_ids_to_titles = pd.read_csv("../data/cdnos_to_titles.csv")#cochrane_ids_to_titles.csv")

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
        try:
            title = cochrane_ids_to_titles[cochrane_ids_to_titles["ReviewID"] == reference_summary['Cochrane ID']]['Cochrane_Title'].values[0]
        except:
            print("whoops.")
            print(reference_summary['Cochrane ID'])
            import pdb; pdb.set_trace()


        #if math.isnan(title):
        if isinstance(title, float):
            print("no title for {}!".format(reference_summary['Cochrane ID']))
            title = "(no title available)"

 
        c.execute("""INSERT INTO target_summaries (uuid, cochrane_id, title, summary) VALUES (?, ?, ?, ?)""",
                                                        (i, reference_summary['Cochrane ID'], 
                                                        title, target))

    conn.commit()
    conn.close()


def add_sources(sources_path="../data/sources.json"):
    conn, c = connect_to_db()

    #sources_df = pd.read_csv(sources_path)
    sources_df = pd.read_json(sources_path)
    
    #failures = 0 

    for cochrane_id, review_sources in sources_df.iterrows():

        titles = review_sources["Title"]
        abstracts = review_sources["Abstract"]
            
        for title, abstract in zip(titles, abstracts):

            c.execute("""INSERT INTO source_abstract (cochrane_id, title, abstract) VALUES (?, ?, ?)""",
                                                            (cochrane_id, title, abstract)) 
 
    conn.commit()
    conn.close()                                              


def add_system_outputs(sys_id, data_path):
    conn, c = connect_to_db()

    system_df = pd.read_csv(data_path)
    for i, generated_summary in system_df.iterrows():
        generated = generated_summary['Prediction_Summary']
        c.execute("""INSERT INTO generated_summaries (cochrane_id, system_id, summary) VALUES (?, ?, ?)""",
                                                        (generated_summary['Cochrane ID'], 
                                                        sys_id, generated))

    conn.commit()
    conn.close()


add_references()
#add_system_outputs("BART-none-abs-title", "../data/output_abs_title.csv")
#add_system_outputs("BART-none-abs_title", "../data/output_abs_title.csv")
#add_system_outputs("BART-XSUM-FT_abs-abs_title", "../data/output_XSUM-FT_abs-abs_title.csv")

#add_system_outputs("BART-none-abs-title", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_abs_title_1024.csv")
add_system_outputs("XSUM-none-abs-title", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_abs_title_xsum.csv")
add_system_outputs("XSUM-FT_abs-abs-title", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-abs_title.csv")
add_system_outputs("XSUM-FT_abs-decorated-abs-title", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-Decorated_input.csv")

add_sources()



