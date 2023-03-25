from top2vec import Top2Vec
import sqlite3


def main():
    conn = sqlite3.connect('congressional_speeches.db')
    res = conn.execute("""SELECT content FROM speeches
                          WHERE LENGTH(content) >= 250
                          ORDER BY RANDOM()""")
    docs = [speech[0] for speech in res]

    model = Top2Vec(docs,
                    ngram_vocab=True,
                    embedding_model='universal-sentence-encoder',
                    # topic_merge_delta=1e-117,
                    workers=2)
    model.save('full.model')
    conn.close()


if __name__ == "__main__":
    main()
