
import math 
import string 
import re

import json 

import pandas as pd 
import sqlite3

db_path = "../data/summaries.db"  
cochrane_ids_to_titles_d = json.load(open("../data/cdno_title.json")) #pd.read_json("../data/cdno_title.json") #pd.read_csv("../data/cdnos_to_titles.csv")#cochrane_ids_to_titles.csv")
c_ids, titles = [], []
for c_id, title in cochrane_ids_to_titles_d.items():
    c_ids.append(c_id)
    titles.append(title)


cochrane_ids_to_titles = pd.DataFrame({"ReviewID":c_ids, 
                                       "Cochrane_Title":titles})

# it is sometimes hard to read the cochrane main findings due to 
# abbreviations which were introduced earlier in the same abstract
# (but not in the main findings); so we expand these here.
abbrevs = json.load(open("../data/cdno_abbrevs.json"))

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
        c_id = reference_summary['Cochrane ID']
        try:
            title = cochrane_ids_to_titles[cochrane_ids_to_titles["ReviewID"] == c_id]['Cochrane_Title'].values[0]
        except:
            print("whoops.")
            print(c_id)
            import pdb; pdb.set_trace()


        if isinstance(title, float):
            print("no title for {}!".format(c_id))
            title = "(no title available)"

    
        target = expand_abbrevs(target, c_id)
        
        c.execute("""INSERT INTO target_summaries (uuid, cochrane_id, title, summary) VALUES (?, ?, ?, ?)""",
                                                        (i, c_id, 
                                                        title, target))

    conn.commit()
    conn.close()


def expand_abbrevs(abstract, cdno):
    expanded = abstract
    for abbrev, expansion in abbrevs[cdno].items():
        # this is very naive but hopefully does the trick
        
        #expanded = " ".join([replacement_str if t.strip(string.punctuation) == abbrev else t for t in expanded.split(" ")])

        replacement_str = "{} ({})".format(abbrev, expansion)
        expanded = re.sub(r"\b{}\b".format(abbrev), replacement_str, expanded)

        # try to handle, e.g., "RCTs" so that we also catch "RCT"
        if abbrev.endswith("s") and expansion.endswith("s"):
            replacement_str = "{} ({})".format(abbrev[:-1], expansion[:-1])
            expanded = re.sub(r"\b{}\b".format(abbrev[:-1]), replacement_str, expanded)

    #print (abbrevs[cdno].items())
    #print (expanded)
    #print ("\n")
    return expanded


def add_sources(sources_path="../data/sources.json"):
    conn, c = connect_to_db()

    sources_df = pd.read_json(sources_path)
    
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

# just XSUM
add_system_outputs("XSUM-None-abs_title", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-None-abs_title.csv")

# XSUM + PMC pre-training 
add_system_outputs("XSUM-FT_abs-abs_title", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-abs_title.csv")

# XSUM + PMC pre-training + pl decoration
add_system_outputs("XSUM-FT_abs-Decorated_input", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-Decorated_input.csv")

# XSUM + PMC pre-training + sort inputs by RoB*N
add_system_outputs("XSUM-FT_abs-robXss_sorted_input", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-robXss_sorted_input.csv")

# XSUM + PMC pre-training + sort inputs by RoB*N + pl decoration
add_system_outputs("XSUM-FT_abs-robXss_sorted_input_dec_pl", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-robXss_sorted_input_dec_pl.csv")

# CD004334 only has 3 ???!!!!

#add_system_outputs("XSUM-FT_abs-abs_title_decorated_plPICOsign", "/Users/byronwallace/code/PubMed_Summary/Evaluation/output_XSUM-FT_abs-decorated_input_plPICOsign.csv")

add_sources()



