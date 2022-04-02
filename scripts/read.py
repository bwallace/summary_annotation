import sqlite3
from random import shuffle

db_path = "../data/summaries_test.db" 

with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        '''uuids = [1310, 498, 904, 92, 1716]
        labels = {'relevance': 0, 'fluency' : 0, 'direction': 0, 'int_faithful': 0, 'out_faithful':0 ,'factuality': 0}
        labels_func = {}
        for uid in uuids:
            uid_labels = cur.execute("""SELECT label_type FROM label WHERE %d == label.generated_summary_id"""%(uid)).fetchall()
            print(uid_labels)
            label_types = [each[0].split('-')[-1].strip() for each in uid_labels]

            for each in label_types:
                labels[each] += 1

        print(labels)'''
        cur.execute('SELECT * FROM LABEL ORDER BY uuid')
        #cur.execute("""SELECT * FROM label WHERE generated_summaries.uuid = label.generated_summary_id""")
        '''cur.execute("""SELECT uuid FROM generated_summaries WHERE NOT 4 = (
                    SELECT COUNT(*) FROM label WHERE generated_summaries.uuid = label.generated_summary_id) 
                    ORDER BY COCHRANE_ID, RANDOM() LIMIT 1;""".format(4))'''
        rows = cur.fetchall()
        for row in rows:
            print(row)
        '''for row in rows:
            uuid, generated_summary_id, label_type, score = row[0], row[1], row[2], row[3]
            print( label_type, score)
            
            cur.execute("""SELECT uuid, summary, system_id FROM generated_summaries where uuid='{}';""".format(generated_summary_id))
            all_fetched = cur.fetchall()
            

            print(all_fetched)
            print( label_type, score)
            print('=' * 13)'''
