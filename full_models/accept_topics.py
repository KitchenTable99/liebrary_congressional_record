import openai
import time
from tqdm import tqdm
import logging
from decouple import config
import pickle
from enum import Enum
import tiktoken

class TopicDesignation(Enum):
    TRASH = 1,
    KEEP = 2


def get_ynh(words):
    user_input = input(f'Should this topic be [t]rashed or [k]ept?\n{words}\n')
    if user_input.lower().startswith('t'):
        return TopicDesignation.TRASH
    elif user_input.lower().startswith('k'):
        return TopicDesignation.KEEP
    else:
        print('You must answer with something beginning with [t/k]')
        return get_ynh(words)


def ask_gpt(prompt):
    attempts = 0
    response = None
    while attempts <= 5:
        try: 
            response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=100)
            logging.info(response)
            attempts = 6
        except KeyboardInterrupt as e:
            raise e
        except:
            attempts += 1
            retry_seconds = 5 * attempts
            print(f"OpenAI error on attempt {attempts}... Retring after {retry_seconds} seconds...")

    if response is None:
        logging.critical('Unable to get response for' + prompt)

    return response if response else []


def main():
    openai.api_key = config('OPENAI_API_KEY')

    # model = Top2Vec.load('./deep_doc2vec.model')
    with open('./tweet_words.pickle', 'rb') as fp:
        topic_words = pickle.load(fp)

    # topic_designations = []
    # for idx, words in enumerate(topic_words):
    #     designation = get_ynh(words)
    #     topic_designations.append(designation)
    #     logging.info(f'{idx}:{designation}')
    # with open('designation.pickle', 'wb') as fp:
    #     pickle.dump(topic_designations, fp)
    # with open('designation.log', 'r') as fp:
    #     data = fp.read()

    with open('./designation.pickle', 'rb') as fp:
        entries = pickle.load(fp)
    keep = [entry == TopicDesignation.KEEP for entry in entries]
    keep_idx = [idx for idx, i in enumerate(keep) if i]
    print(keep_idx)
    return

    gpt_responses = []
    for idx in tqdm(keep_idx):
        words = topic_words[idx]
        joined_words = ' '.join(words)
        prompt = 'What is the topic represented by these words: ' + joined_words
        gpt_responses.append(ask_gpt(prompt))
    with open('responses.pickle', 'wb') as fp:
        pickle.dump(gpt_responses, fp)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='designation.log')
    main()
