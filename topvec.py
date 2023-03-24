from top2vec import Top2Vec
import sqlite3


def main():
    conn = sqlite3.connect('test.db')
    docs = [speech[0] for speech in conn.execute('SELECT content FROM speeches LIMIT 10')]

    model = Top2Vec(docs,
                    ngram_vocab=True,
                    embedding_model='all-MiniLM-L6-v2',
                    workers=3)
    model.save('test.model')

if __name__ == "__main__":
    main()
