from mongodb_client import DB
import log_analysis
import utils
import os


class Analyzer:
    def __init__(self):
        self.db = DB()
        self.object_list = []       # list of mongodb identifiers
        self.processed = {}         # False = not analyzed

    def _acquire_object_id_list(self):
        self.object_list = self.db.get_all_inserted()
        self.processed = dict.fromkeys(self.object_list, False)

    def do_log_analysis(self, logfile):
        if len(self.object_list) == 0:
            self._acquire_object_id_list()
        log_analysis.plot_distributions(logfile)
        self.compute_ratio_rev_contrib()
        log_analysis.plot_ratio_rev_contrib()
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

    def analyze(self, objectid):
        failed = []
        doc = self.db.get_document(object_id=objectid)
        name = doc['name']
        out_dir = self.prepare_dest_folder(name)
        dates = doc['important_dates']
        df = doc['df']
        stationarity_file = 'results/stationarity.txt'
        out_stat = open(stationarity_file, 'a')
        for col in list(df.columns.values):
            ts = df[col]
            utils.plot_ts(ts, "{}:{}".format(name, col), os.path.join(out_dir, "orig_{}.pdf".format(col)))
            stationarity = utils.is_stationary(ts)
            out_stat.write("{} - ts: {} - len: {} - Stationary: {}\n".format(name, col, len(ts), stationarity))
            if stationarity:
                lag_acf, lag_pacf = utils.find_acf_pacf(ts, fname=os.path.join(out_dir, '{}_acf_pacf.pdf'.format(col)))
            else:
                ts_diff = utils.differentiate(ts)
                diff_stationarity = utils.is_stationary(ts_diff)
                out_stat.write("{} - ts_diff: {} - len: {} - Stationary: {}\n".format(name, col, len(ts_diff), diff_stationarity))
                if diff_stationarity:
                    lag_acf, lag_pacf = utils.find_acf_pacf(ts_diff, fname=os.path.join(out_dir, '{}_diff_acf_pacf.pdf'.format(col)))
                else:
                    ts_log = utils.log_transform(ts)
                    log_stationarity = utils.is_stationary(ts_log)
                    out_stat.write("{} - ts_log: {} - len: {} - Stationary: {}\n".format(name, col, len(ts_log), log_stationarity))
                    if log_stationarity:
                        lag_acf, lag_pacf = utils.find_acf_pacf(ts_diff, fname=os.path.join(out_dir, '{}_log_acf_pacf.pdf'.format(col)))
                    else:
                        out_stat.write("{} - ts: {} - len: {} - Stationary: 1st order failed\n".format(name, col, len(ts)))
                        failed.append(objectid)


    def prepare_dest_folder(self, name):
        out_dir = 'results/people/{}'.format(name)
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        return out_dir


if __name__ == "__main__":
    a = Analyzer()
    logfile = 'data/logfile.txt'
    a.do_log_analysis(logfile)
    dic = log_analysis.find_longest_ts(logfile, larger_than=130)
    print("Starting the analysis of {} ts".format(len(dic)))
    for obj in dic:
        a.analyze(obj)

