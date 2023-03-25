import sqlite3
import itertools
from top2vec import Top2Vec
import sys


def get_conn(testing=True):
    return sqlite3.connect(':memory:') if testing else sqlite3.connect('topic_models.db')

def extract_topics_from_model(model):
    sizes, topic_nums = model.get_topic_sizes()
    to_return = []
    for size, topic_num in zip(sizes, topic_nums):
        content_array, _, doc_ids = model.search_documents_by_topic(topic_num, size)
        to_return.extend(zip(doc_ids, content_array, itertools.repeat(topic_num)))

    return to_return



def main():
    conn = get_conn()
    model_name = sys.argv[1]
    model = Top2Vec.load(f'{model_name}.model')

    conn.execute(f"""CREATE TABLE IF NOT EXISTS temp_{model_name}(
                     temp_id INTEGER PRIMARY KEY
                     content TEXT,
                     topic_num INTEGER
                     )""")
    labeled_speeches = extract_topics_from_model(model)
    print(labeled_speeches)




if __name__ == "__main__":
    main()
