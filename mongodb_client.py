import pickle
from pymongo import MongoClient
from bson.binary import Binary
from person_page import PersonPage


class DB:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.webts
        self.persons = self.db.persons

    def insert_person(self, personpage):
        pickled = pickle.dumps(personpage.__dict__)
        person_page_id = self.persons.insert_one({'bin-data': Binary(pickled)}).inserted_id
        return person_page_id

    def get_all_inserted(self):
        l = self.persons.distinct('_id')
        print(l)


if __name__ == "__main__":
    d = DB()
    d.get_all_inserted()


