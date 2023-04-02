import logging
from os import close
import time
import threading
from queue import Queue
import sqlite3
import difflib
from pprint import pprint


names_queue, close_match_queue = Queue(), Queue()


def get_names():
    leg_conn = sqlite3.connect('./legislators.db')
    leg_conn.execute("ATTACH DATABASE 'congressional_speeches.db' as cs")
    cur = leg_conn.execute("""SELECT full_name
                              FROM members
                              INNER JOIN cs.speakers
                              ON cs.speakers.bioguide=members.bioguide
                              WHERE full_name IS NOT NULL""")
    null_cur = leg_conn.execute("""SELECT first_name, last_name
                              FROM members
                              INNER JOIN cs.speakers
                              ON cs.speakers.bioguide=members.bioguide
                              WHERE full_name IS NULL""")
    names_who_spoke = [res[0] for res in cur.fetchall()]
    names_who_spoke.extend([f'{res[0]} {res[1]}' for res in null_cur.fetchall()])

    twit_conn = sqlite3.connect('./user_info.db')
    cur = twit_conn.execute('SELECT name FROM users WHERE name IS NOT NULL') # any good congressional account would have a name
    twitter_names = [res[0] for res in cur.fetchall()]

    return names_who_spoke, twitter_names


def list_to_gen(list_):
    yield from list_


def make_matches(twitter_names):
    while True:
        if close_match_queue.qsize() < 20:
            name = names_queue.get()
            close_names = difflib.get_close_matches(name, twitter_names, n=5)
            close_match_queue.put((name, close_names))


def get_choice(name, matches):
    print(name)
    print(matches)

    return input()


def log_corresponding(name, matches, what_to_do):
    keep_up_to = 0
    try:
        keep_up_to = int(what_to_do)
    except ValueError:
        keep_up_to = -1

    if keep_up_to != -1:
        keep_matches = matches[:keep_up_to]
    else:
        match_idx = [l_num for l_num, l in enumerate('abcde') if l in what_to_do]
        keep_matches = [match for match_ix, match in enumerate(matches) if match_ix in match_idx]

    logging.info(f'{name}:{keep_matches}')


def main():
    testing = False
    who_spoke, twitter_names = get_names()

    if testing:
        who_spoke = who_spoke[:10]

    for name in who_spoke:
        names_queue.put(name)

    threading.Thread(target=make_matches, args=[twitter_names], daemon=True).start()

    while not names_queue.empty() or not close_match_queue.empty():
        name, matches = close_match_queue.get()
        what_to_do = get_choice(name, matches)
        log_corresponding(name, matches, what_to_do)


if __name__ == "__main__":
    logging.basicConfig(filename='choice.log', level=logging.INFO)
    main()
