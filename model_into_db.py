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
        content_array, _, doc_ids = model.search_documents_by_topic(topic_num, size)
        yield list(zip(doc_ids.tolist(), content_array.tolist(), itertools.repeat(int(topic_num))))


def write_speeches(labeled_speeches, conn, table):
    for insert_block in labeled_speeches:
        logging.debug(f'inserting into {table}')
        logging.debug(f'{insert_block[0] = }')
        logging.debug(f'{type(insert_block[0][0]) = }')
        logging.debug(f'{type(insert_block[0][1]) = }')
        logging.debug(f'{type(insert_block[0][2]) = }')
        with conn:
            conn.executemany(f'INSERT INTO {table}(temp_id, content, topic_num) VALUES(?, ?, ?)', insert_block)


def main():
    conn = get_conn(testing=False)
    model_name = sys.argv[1]
    model = Top2Vec.load(f'{model_name}.model')

    conn.execute(f"""CREATE TABLE IF NOT EXISTS temp_{model_name}(
                     temp_id INTEGER PRIMARY KEY,
                     content TEXT,
                     topic_num INTEGER
                     )""")
    labeled_speeches = extract_topics_from_model(model)
    write_speeches(labeled_speeches, conn, f'temp_{model_name}')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
