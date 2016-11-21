#!/usr/bin/python3
import os
from sparqlclient import SparqlClient
import re
import pandas as pd
import json
import analysis
from collections import defaultdict


def convert_date(datestring, month=False):
    if month:
        return pd.to_datetime(datestring, format="%m/%Y")
    else:
        return pd.to_datetime(datestring, format="%Y")


def extract(dic, search_string):
    temp_dic = defaultdict(list)
    tmp = []
    target = [v for k, v in dic.items() if re.search(search_string, k)][0]
    for el in target:
        tmp.append([v['value'] for k, v in el.items() if not re.match('http:', v['value'])])
    for nodeid, value in tmp:
        if re.match('nodeID', value):  # swap if nodeid in second place
            nodeid, value = value, nodeid
        assert re.match('nodeID', nodeid)
        try:
            transformed = float(value)
        except ValueError:
            transformed = convert_date(value, month=True)
        temp_dic[nodeid].append(transformed)

    extracted = {}
    for k, v in temp_dic.items():
        num, date = v
        extracted[date] = {search_string: num, "{}_nodeid".format(search_string): k}
    return extracted


def execute_query(url, q, fname):
    s = SparqlClient(url)
    res = s.run_query(q)
    with open(fname, 'w') as outfile:
        json.dump(res, outfile)
    return res


def create_dataframe(dic, search_string_list):
    list_of_df = []
    for ss in search_string_list:
        extracted = extract(dic, ss)
        list_of_df.append(pd.DataFrame.from_dict(extracted, orient='index'))
    return pd.concat(list_of_df, axis=1)


def analyze(df, keys):
    resultdir = './results'
    for k in keys:
        ts = df[k]
        adftest = analysis.adf(ts, fname=os.path.join(resultdir, "rolling_stats_{}.png".format(k)))
        print("Stationarity {}: {}".format(k,
                                           adftest[1] < 0.5 and any([v > adftest[0] for k, v in adftest[4].items()])))
        print("max value at {}:  {}".format(df[k].idxmax(), df[k].loc[df[k].idxmax()]))
        if not analysis.is_stationary(ts):
            ts_diff = analysis.differentiate(ts)
            print("Differenced {}: {}".format(k, analysis.is_stationary(ts_diff)))
            acf, pacf = analysis.find_acf_pacf(ts_diff, fname=os.path.join(resultdir, "acf_pacf_diff_{}.png".format(k)))
            print(acf)

if __name__ == "__main__":
    import time
    expire_time = 60 * 60 * 24 * 7  # 7 days
    datafile = 'hillary_clinton.json'
    if not os.path.isfile(datafile) or time.time() - os.stat(datafile).st_mtime > expire_time:
        print("Querying URL")
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
        print("Querying Local")
        with open(datafile) as infile:
            res = json.load(infile)

    if len(res.keys()) == 0:
        exit("Problems loading data")
    print("DF length: {}".format(len(res['results']['bindings'])))

    p_keys = {}
    for el in res['results']['bindings']:
        p_key = el['p']['value']
        if p_key not in p_keys:
            p_keys[p_key] = [el]
        else:
            p_keys[p_key].append(el)

    regex_keys = ['revPerMonth', 'averageSizePerMonth']
    df = create_dataframe(p_keys, regex_keys)
    analyze(df, regex_keys)
    # ts_num = TS('num', df.num)
    # print("ts_num is Stationary: {}".format(ts_num.is_stationary()))
    # ts_msize = TS('msize', df.msize)
    # print("ts_msize is Stationary: {}".format(ts_msize.is_stationary()))
    # ts_num.transform()




