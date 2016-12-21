from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError
from urllib.error import HTTPError

query_all_person = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX type: <http://dbpedia.org/class/yago/>
    PREFIX prop: <http://dbpedia.org/ontology/>

    SELECT DISTINCT * WHERE {
        ?person a dbpedia-owl:Person
    }
    """

query_history = "SELECT DISTINCT * WHERE {<http://fr.wikipedia.org/wiki/%s> ?p ?v . OPTIONAL {?v ?p2 ?v2} } ORDER BY ?v"


class SparqlClient:
    def __init__(self, url="http://dbpedia-historique.inria.fr/sparql"):
        self.sparql = SPARQLWrapper(url)

    def get_history_per_person(self, person, format=JSON):
        try:
            self.sparql.setQuery(query_history % person)
            self.sparql.setReturnFormat(format)
            return self.sparql.query().convert()
        except HTTPError as e:
            print("HTTPError {}  ({}) ".format(person, e))
            return None
        except EndPointInternalError as e:
            print("EndpointInternalError {}  ({}) ".format(person, e))
            return None

    def get_all_people(self, format=JSON):
        people = []
        self.sparql.setQuery(query_all_person)
        self.sparql.setReturnFormat(format)
        res = self.sparql.query().convert()
        for el in res['results']['bindings']:
            url = el['person']['value']
            person = url.split("/")[-1]
            people.append(person)
        return people


if __name__ == "__main__":
    s = SparqlClient()
    people = s.get_all_people()
    print("Fetched {} people".format(len(people)))
    person = people[0]
    res = s.get_history_per_person(person)
    print(res)


