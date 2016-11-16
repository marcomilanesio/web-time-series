from sparqlclient import SparqlClient
import re
import pandas as pd
import json
from ts import TS


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


def execute_query(url, q, fname):
    s = SparqlClient(url)
    res = s.run_query(q)
    with open(fname, 'w') as outfile:
        json.dump(res, outfile)
    return res


def create_dataframe(dic):
    # regex_keys = ['revPerMonth', 'averageSizePerMonth']
    rev_per_month = [v for k, v in dic.items() if re.search('revPerMonth', k)][0]
    size_per_month = [v for k, v in dic.items() if re.search('averageSizePerMonth', k)][0]

    rev = extract(rev_per_month)
    size = extract(size_per_month)

    n_rev = dict((v[1], {'num': v[0], 'nodeId_n': k}) for k, v in rev.items())
    n_size = dict((v[1], {'size': v[0], 'nodeId_s': k}) for k, v in size.items())

    df_rev = pd.DataFrame.from_dict(n_rev, orient='index')
    df_size = pd.DataFrame.from_dict(n_size, orient='index')

    return pd.concat([df_rev, df_size], axis=1)


if __name__ == "__main__":
    import os
    import time
    expire_time = 60 * 60 * 24 * 2  # 2 days
    datafile = 'hillary_clinton.json'
    if not os.path.isfile(datafile) or time.time() - os.stat(datafile).st_mtime > expire_time:
        print("Query")
        q = """ SELECT DISTINCT * WHERE
            {
              <http://fr.wikipedia.org/wiki/Hillary_Clinton> ?p ?v .
              OPTIONAL {?v ?p2 ?v2}
            }
            ORDER BY ?v
            """
        url = "http://dbpedia-historique.inria.fr/sparql"
        res = execute_query(url, q, datafile)
    else:
        print("Local")
        with open(datafile) as infile:
            res = json.load(infile)

    if len(res.keys()) == 0:
        exit("Problems loading data")
    print(len(res))

    p_keys = {}
    for el in res['results']['bindings']:
        p_key = el['p']['value']
        if p_key not in p_keys:
            p_keys[p_key] = [el]
        else:
            p_keys[p_key].append(el)

    df = create_dataframe(p_keys)
    print(df.head())
    ts_num = TS('num', df.num)
    print("ts_num is Stationary: {}".format(ts_num.is_stationary()))
    ts_size = TS('size', df.size)
    print("ts_size is Stationary: {}".format(ts_size.is_stationary()))




