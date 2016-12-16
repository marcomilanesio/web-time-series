from collections import defaultdict
import re
import pandas as pd

regex_keys = ['revPerMonth', 'averageSizePerMonth']


class DataCleaner:
    def __init__(self, data):
        self.data = data
        self.df = None

    def _convert_date(self, datestring, month=False):
        if month:
            return pd.to_datetime(datestring, format="%m/%Y")
        else:
            return pd.to_datetime(datestring, format="%Y")

    def _extract(self):
        nodeid_dic = {}
        for dic in self.data:       # first, from data to {nodeid: [num, timestamp]}
            for k, v in dic.items():
                if re.search('revPerMonth', v['value']):
                    nodeid = dic['v']['value']
                    if nodeid not in nodeid_dic:
                        nodeid_dic[nodeid] = {'num_rev': 0, 'month': 0, 'size_rev': 0}
                    value_string = dic['v2']['value']
                    try:
                        value = int(value_string)
                        nodeid_dic[nodeid]['num_rev'] = value
                    except ValueError:
                        value = self._convert_date(value_string, month=True)
                        nodeid_dic[nodeid]['month'] = value

                elif re.search('averageSizePerMonth', v['value']):
                    nodeid = dic['v']['value']
                    if nodeid not in nodeid_dic:
                        nodeid_dic[nodeid] = {'num_rev': 0, 'month': 0, 'size_rev': 0}
                    value_string = dic['v2']['value']
                    try:
                        value = float(value_string)
                        nodeid_dic[nodeid]['size_rev'] = value
                    except ValueError:
                        value = self._convert_date(value_string, month=True)
                        nodeid_dic[nodeid]['month'] = value

        assert [re.match('nodeID', k) for k in nodeid_dic]
        time_dic = {}           # second, from {nodeid: [num, timestamp, size]} to {timestamp: {num, size}}
        for _, v in nodeid_dic.items():
            if v['month'] not in time_dic:
                time_dic[v['month']] = {'num_rev': 0, 'size_rev': 0}
            time_dic[v['month']]['num_rev'] += v['num_rev']
            time_dic[v['month']]['size_rev'] += v['size_rev']
        return time_dic

    def create_dataframe(self):
        dic = self._extract()
        self.df = pd.DataFrame.from_dict(dic, orient='index')




if __name__ == "__main__":
    from sparql_client import SparqlClient
    s = SparqlClient()
    people = s.get_all_people()
    print("Fetched {} people".format(len(people)))
    person = people[0]
    res = s.get_history_per_person(person)
    data = res['results']['bindings']  # List of dictionaries

    d = DataCleaner(data)
    d.create_dataframe()

