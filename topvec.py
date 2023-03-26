from top2vec import Top2Vec
import sqlite3


def main():
    conn = sqlite3.connect('/datasets/do-not-delete--liebrary-of-congress/congressional_speeches.db')
    cursor = conn.execute("""SELECT id, content
                             FROM speeches
                             WHERE LENGTH(content) >= 250
                             GROUP BY content""")
    ids, docs = zip(*cursor.fetchall())
    conn.close()

    model = Top2Vec(list(docs),
                    document_ids=list(ids),
                    ngram_vocab=True,
                    embedding_model='universal-sentence-encoder',
                    workers=10)
                    # topic_merge_delta=1e-117)
    model.save('universal_sentence.model')


if __name__ == "__main__":
    main()
