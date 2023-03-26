import sqlite3
import itertools
import logging
from typing import List
from speech_extractor import Speech, PartialCongressDay
import glob


def get_connection(testing: bool = True) -> sqlite3.Connection:
    if testing:
        return sqlite3.connect(':memory:')
    else:
        return sqlite3.connect('congressional_speeches.db')


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(""" CREATE TABLE IF NOT EXISTS speakers(
                bioguide TEXT PRIMARY KEY,
                name     TEXT,
                UNIQUE(bioguide, name)
                ) """)
    cur.execute(""" CREATE TABLE IF NOT EXISTS speeches(
                id               INTEGER PRIMARY KEY,
                date             INTEGER,
                speaker_bioguide TEXT,
                chamber          INTEGER,
                content          TEXT,
                FOREIGN KEY(speaker_bioguide) REFERENCES speakers(bioguide)
                ) """)

def insert_into_speaker_table(speeches: List[Speech], conn: sqlite3.Connection) -> None:
    data = [(speech.speaker_bioguide, speech.speaker_name) for speech in speeches]
    with conn:
        conn.executemany("INSERT OR IGNORE INTO speakers VALUES(?, ?)", data)


def insert_into_speeches_table(speeches: List[Speech], date: int, chamber: int, conn: sqlite3.Connection) -> None:
    repeated_date = itertools.repeat(date)
    repeated_chamber = itertools.repeat(chamber)
    speaker_bioguide = (speech.speaker_bioguide for speech in speeches)
    content = (speech.content for speech in speeches)

    data = list(zip(repeated_date, speaker_bioguide, repeated_chamber, content))
    if data == []:
        return

    with conn:
        conn.executemany("INSERT INTO speeches(date, speaker_bioguide, chamber, content) VALUES(?, ?, ?, ?)", data)


def main():
    logging.basicConfig(level=logging.WARNING)
    conn = get_connection(testing=False)
    create_tables(conn)

    all_files = glob.glob('./*/**', recursive=True)
    for file in all_files:
        if '.json' in file:
            pdc = PartialCongressDay(file)
            speeches = pdc.get_speeches()
            date = pdc.get_date()
            chamber = pdc.get_chamber()

            insert_into_speaker_table(speeches, conn)
            insert_into_speeches_table(speeches, date, chamber, conn)

    # for row in conn.cursor().execute("SELECT * FROM speakers WHERE bioguide IS NULL"):
    #     print(row)

    conn.close()


if __name__ == "__main__":
    main()
