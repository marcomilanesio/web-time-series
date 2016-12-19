from pymongo import MongoClient
from person_page import PersonPage


class DB:
    def __init__(self, dbname='webts'):
        self.client = MongoClient()
        self.db = self.client.dbname
        self.persons = self.db.persons

    def insert_person(self, personpage):
        personpage_id = self.persons.insert_one(personpage)
        return personpage_id
