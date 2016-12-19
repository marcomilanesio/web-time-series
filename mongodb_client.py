import pickle
from bson.binary import Binary
from pymongo import MongoClient
from person_page import PersonPage


class DB:
    def __init__(self, dbname='webts'):
        self.client = MongoClient()
        self.db = self.client.dbname
        self.persons = self.db.persons

    def insert_person(self, personpage):
        person_page_id = self.persons.insert_one({'bin_data': Binary(pickle.dumps(personpage))})
        return person_page_id
