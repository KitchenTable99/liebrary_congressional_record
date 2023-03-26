import sqlite3
import logging
import itertools
from top2vec import Top2Vec
import sys


def get_conn(testing=True):
    logging.debug(f'Creating conn object with {testing = }')
    return sqlite3.connect(':memory:') if testing else sqlite3.connect('topic_models.db')


def extract_topics_from_model(model):
    sizes, topic_nums = model.get_topic_sizes()
    for size, topic_num in zip(sizes, topic_nums):
        _, _, doc_ids = model.search_documents_by_topic(topic_num, size)
        yield list(zip(doc_ids.tolist(), itertools.repeat(int(topic_num))))


def write_speeches(labeled_speeches, conn, table):
    for insert_block in labeled_speeches:
        logging.debug(f'{insert_block[0][0] = }')
        with conn:
            conn.executemany(f'INSERT INTO {table}(speech_id, topic_num) VALUES(?, ?)', insert_block)


def main():
    conn = get_conn(testing=False)
    model_name = sys.argv[1]
    model = Top2Vec.load(f'full_models/{model_name}.model')

    # speech_id is a foreign key, but to a table in a different database, but that isn't supported in sqlite
    conn.execute(f"""CREATE TABLE IF NOT EXISTS {model_name}(
                     topic_model_id INTEGER PRIMARY KEY,
                     speech_id INTEGER,
                     topic_num INTEGER
                     )""")
    labeled_speeches = extract_topics_from_model(model)
    write_speeches(labeled_speeches, conn, model_name)

    # for row in conn.execute(f"""SELECT * FROM universal_sentence LIMIT 10"""):
    #     print(row)
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
