from mongodb_client import DB


class Analyzer:
    def __init__(self):
        self.db = DB()
        self.object_list = []       # list of mongodb identifiers
        self.processed = {}         # False = not analyzed

    def _acquire_object_id_list(self):
        self.object_list = self.db.get_all_inserted()
        self.processed = dict.fromkeys(self.object_list, False)

    def do_analysis(self):
        if len(self.object_list) == 0:
            self._acquire_object_id_list()
        # self.compute_ratio_rev_contrib()
        self.find_last_update()

    def compute_ratio_rev_contrib(self):
        ratios = []
        for object_id in self.object_list:
            dic = self.db.get_document(object_id)
            ratio = float(sum(dic['df'].num_rev) / dic['unique_contributors'])
            ratios.append((object_id, ratio))
        with open('data/ratio_rev_contrib.txt', 'w') as out:
            for tup in ratios:
                out.write("{}\n".format(str(tup)))

    def find_last_update(self):
        max_date = None
        for object_id in self.object_list:
            dic = self.db.get_document(object_id)
            if not max_date or dic['df'].index[-1] > max_date:
                max_date = dic['df'].index[-1]
        print("Last update: {}".format(max_date))

if __name__ == "__main__":
    a = Analyzer()
    a.do_analysis()


