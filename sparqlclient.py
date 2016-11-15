from SPARQLWrapper import SPARQLWrapper, JSON


class SparqlClient:
    def __init__(self, url):
        self.sparql = SPARQLWrapper(url)

    def run_query(self, q, format=JSON):
        self.sparql.setQuery(q)
        self.sparql.setReturnFormat(format)
        return self.sparql.query().convert()
