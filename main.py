from sparqlclient import SparqlClient
import re
import pandas as pd


def convert_date(datestring, month=False):
    if month:
        return pd.to_datetime(datestring, format="%m/%Y")
    else:
        return pd.to_datetime(datestring, format="%Y")


def extract(l):
    res = {}
    for el in l:
        tmp = [v['value'] for k, v in el.items() if not re.match('http:', v['value'])]
        k = tmp[0]
        v = tmp[1]
        if re.match('node', k):
            if k not in res:
                res[k] = []
            try:
                num = float(v)
                res[k].append(num)
            except ValueError:
                date = convert_date(v, month=True)
                res[k].append(date)
    return res


q = """
    SELECT DISTINCT * WHERE
    {
      <http://fr.wikipedia.org/wiki/Hillary_Clinton> ?p ?v .
      OPTIONAL {?v ?p2 ?v2}
    }
    ORDER BY ?v
    """
url = "http://dbpedia-historique.inria.fr/sparql"
s = SparqlClient(url)
res = s.run_query(q)

p_keys = {}
for el in res['results']['bindings']:
    p_key = el['p']['value']
    if p_key not in p_keys:
        p_keys[p_key] = [el]
    else:
        p_keys[p_key].append(el)

regex_keys = ['revPerMonth', 'averageSizePerMonth']
rev_per_month = [v for k, v in p_keys.items() if re.search('revPerMonth', k)][0]
size_per_month = [v for k, v in p_keys.items() if re.search('averageSizePerMonth', k)][0]

rev = extract(rev_per_month)
size = extract(size_per_month)

print(size)

