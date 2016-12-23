import pickle
from pymongo import MongoClient
from bson.objectid import ObjectId


class DB:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.webts
        self.people = self.db.people

    def insert_person(self, personpage):
        pickled = pickle.dumps(personpage.__dict__)
        person_page_id = self.people.insert_one({'pickled': pickled}).inserted_id
        return person_page_id

    def get_all_inserted(self):
        return self.people.distinct('_id')

    def get_document(self, object_id):
        match = self.people.find_one({"_id": ObjectId(object_id)})
        pickled = match['pickled']
        res = pickle.loads(pickled)
        return res


if __name__ == "__main__":
    d = DB()
    l = d.get_all_inserted()
    _id = l[0]
    doc = d.get_document(_id)
    print(type(doc['df']))



