import json
from datetime import datetime
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

TEST_JSON = './2017/CREC-2017-11-15/json/CREC-2017-11-15-pt1-PgH9268-3.json'

@dataclass
class Speech:
    speaker_bioguide: str
    speaker_name: str
    content: str

    @staticmethod
    def get_special_bioguide(name):
        if 'VICE PRESIDENT' in name:
            return 'VicePresident'
        elif 'The PRESIDING OFFICER' in name:
            return 'PresidingOfficer'
        elif 'The ACTING CHAIR' in name:
            return 'ActingChair'
        elif 'The SPEAKER' in name:
            return 'Speaker'
        elif 'The SPEAKER pro tempore' in name:
            return 'SpeakerProTem'
        elif 'The PRESIDENT pro tempore' in name:
            return 'PresProTem'
        elif 'The ACTING PRESIDENT pro tempore' in name:
            return 'ActingPresProTem'
        else:
            return None



class PartialCongressDay:

    def __init__(self, file_path) -> None:
        logging.info(f'Creating PDC object for {file_path}')
        self.file_path = file_path
        with open(file_path, 'r') as fp:
            self.json_data = json.load(fp)

    def get_date(self) -> int:
        "Returns the number of seconds since the epoch to the day this object describes"
        header = self.extract_field('header', self.json_data)

        month = self.extract_field('month', header)
        year = self.extract_field('year', header)
        day = self.extract_field('day', header)
        padded_day = day.rjust(2, '0')

        date = datetime.strptime(f'{month} {padded_day} {year}', '%B %d %Y')
        logging.debug(f'Parsed date as: {date}')

        return int(date.timestamp())

    def get_chamber(self) -> int:
        """Returns an int representing the chamber where the speeches were given:
            0 --> House of Representatives
            1 --> Senate
        """
        header: Dict = self.extract_field('header', self.json_data)

        chamber = self.extract_field('chamber', header)

        return 0 if chamber == 'House' else 1


    def get_speeches(self) -> List[Speech]:
        "Returns a list of Speech objects representing each speech for the partial congressional day"
        json_content = self.extract_field('content', self.json_data)

        to_return = []
        for speech in json_content:
            kind = self.extract_field('kind', speech)
            if kind != 'speech':
                continue

            speaker_name = self.extract_field('speaker', speech)
            speaker_bioguide = Speech.get_special_bioguide(speaker_name)
            if speaker_bioguide is None:
                speaker_bioguide = self.extract_field('speaker_bioguide', speech, raise_exception=False)
            # TODO: determine if name always first part of speech
            content = self.extract_field('text', speech)

            to_return.append(Speech(speaker_bioguide, speaker_name, content))

        return to_return

    def extract_field(self, field, dictionary, raise_exception=True):
        """Given some dictionary and some field, this will extract the field and raise a ValueError
        if the field is not present. It will return the contents of the field"""
        field_content = dictionary.get(field, None)
        if field_content is None:
            logging.critical(f'{self.file_path} does not have a {field}')

        if field_content is None and raise_exception:
            raise ValueError(f'{field} field missing from {self.file_path}')

        return field_content



def main():
    logging.basicConfig(level=logging.INFO)
    pdc = PartialCongressDay(TEST_JSON)
    # print(json.dumps(pdc.json_data, indent=1))
    # print(pdc.get_day())
    # print(pdc.get_chamber())
    print(pdc.get_speeches())


if __name__ == "__main__":
    main()
