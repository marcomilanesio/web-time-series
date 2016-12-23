import re
import pandas as pd
from person_page import PersonPage

regex_keys = ['revPerMonth', 'averageSizePerMonth']

other_keys = ['uniqueContributorNb', 'birthDate', 'deathDate', 'jusqu\'auFonction']


class DataCleaner:
    def __init__(self, data, person):
        self.data = data
        self.person_page = PersonPage(person)

    def _convert_date(self, datestring, month=False):
        if month:
            return pd.to_datetime(datestring, format="%m/%Y")
        else:
            return pd.to_datetime(datestring, format="%Y")

    def _convert_complete_date(self, datestring):
        try:
            return pd.to_datetime(datestring.split("+")[0], format="%Y-%m-%d", infer_datetime_format=True)
        except:
            return datestring.split("+")[0]

    def get_secondary_keys(self):
        for dic in self.data:
            if 'p2' in dic:
                if re.search('birthDate', dic['p2']['value']):
                    self.person_page.add_birth_date(self._convert_complete_date(dic['v2']['value']))
                if re.search('deathDate', dic['p2']['value']):
                    self.person_page.add_death_date(self._convert_complete_date(dic['v2']['value']))
                if re.search('Fonction', dic['p2']['value']):
                    self.person_page.add_important_date(self._convert_complete_date(dic['v2']['value']))

            if re.search('uniqueContributorNb', dic['p']['value']):
                self.person_page.add_unique_contributors(int(dic['v']['value']))

    def _extract(self):
        nodeid_dic = {}
        self.get_secondary_keys()
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

        if len(nodeid_dic) == 0:
            # print("{} page has no information on revPerMonth".format(self.person_page.name))
            # print("Skipping")
            return None
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
        if not dic:
            # print("unable to create dataframe.")
            self.person_page.add_dataframe(pd.DataFrame.from_dict({}))
        else:
            # self.df = pd.DataFrame.from_dict(dic, orient='index')
            self.person_page.add_dataframe(pd.DataFrame.from_dict(dic, orient='index'))


if __name__ == "__main__":
    from sparql_client import SparqlClient
    from mongodb_client import DB
    import pickle
    import os

    s = SparqlClient()
    people_file = './data/people.txt'
    if not os.path.isfile(people_file):
        people = s.get_all_people()
        # print("Fetched {} people".format(len(people)))
        with open(people_file, 'wb') as fp:
            pickle.dump(people, fp)
    else:
        with open(people_file, 'rb') as fp:
            people = pickle.load(fp)
        # print("Fetched {} people from file".format(len(people)))

    db = DB()
    # TODO 98001 > data/logfile.txt
    for person in people[98001:]:
        res = s.get_history_per_person(person)
        if res is None:
            continue
        data = res['results']['bindings']  # List of dictionaries
        d = DataCleaner(data, person)
        d.create_dataframe()
        if len(d.person_page.df) < 10:
            print("Insufficient data for [{}]: {}".format(d.person_page.name, len(d.person_page.df)))
        else:
            p_id = db.insert_person(d.person_page)
            print("Inserted data for [{} ({})]: {}".format(d.person_page.name, p_id, len(d.person_page.df)))

