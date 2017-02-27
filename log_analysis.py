import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from scipy.stats.kde import gaussian_kde
import re


def compute_stats(lengths):
    with open('results/stats.txt', 'w') as out:
        out.write("Min: {}\n".format(np.min(lengths)))
        out.write("Max: {}\n".format(np.max(lengths)))
        out.write("Mean: {}\n".format(np.mean(lengths)))
        out.write("Std: {}\n".format(np.std(lengths)))
        out.write("Median (50-tile): {}\n".format(np.percentile(lengths, 50)))   # median.
        out.write("95-tile: {}\n".format(np.percentile(lengths, 95)))
        out.write("zero-length: {}\n".format(lengths.count(0)))
        out.write("95-length: {}\n".format(lengths.count(np.percentile(lengths, 95))))
        out.write("max-length: {}\n".format(lengths.count(np.max(lengths))))


def plot_distributions(logfile):
    with open(logfile, 'r') as infile:
        arr = infile.readlines()
        lengths = [int(line.split(":")[1]) for line in arr[1:]]
        lengths.sort()
    compute_stats(lengths)
    figname = './results/distributions.pdf'
    mu = np.mean(lengths)
    std = np.std(lengths)
    cdf = stats.norm.cdf(lengths, mu, std)

    kde = gaussian_kde(lengths)
    dist_space = np.linspace(min(lengths), max(lengths), 100)

    fig, ax1 = plt.subplots()
    pdf_line = ax1.plot(dist_space, kde(dist_space), linestyle='dashed', label="pdf")
    ax1.set_xlabel('length')
    ax1.set_ylabel('P(x)')
    ax2 = ax1.twinx()
    cdf_line = ax2.plot(lengths, cdf, 'r-', label="cdf")
    ax2.set_ylabel('P(x < X)')
    lines = pdf_line + cdf_line
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='best', shadow=True, fancybox=True)
    plt.savefig(figname)
    plt.close()


def plot_ratio_rev_contrib():
    fname = 'data/ratio_rev_contrib.txt'
    with open(fname, 'r') as infile:
        arr = infile.readlines()
    ratios = []
    for el in arr:
        ratios.append(float(el.rstrip()[:-1].split(",")[1].strip()))
    print("rev_contrib: ", np.min(ratios), np.max(ratios), np.mean(ratios), np.std(ratios), np.median(ratios), np.percentile(ratios, 95))
    ratios.sort()
    mu = np.mean(ratios)
    std = np.std(ratios)
    cdf = stats.norm.cdf(ratios, mu, std)
    fig = plt.figure()
    plt.plot(ratios, cdf, 'r-', label="ratio")
    plt.savefig('results/ratio_rev_contrib.pdf')
    plt.close()


def find_longest_ts(logfile, larger_than=150):
    with open(logfile, 'r') as infile:
        arr = infile.readlines()
    res = {}
    regexp = re.compile("[a-z0-9]{24}(?=\))")
    for line in arr[1:]:
        try:
            l = int(line.split(":")[1])
            if l > larger_than:
                try:
                    objid = re.search(regexp, line).group(0)
                    res[objid] = l
                except AttributeError as e:
                    exit("Unable to process {} - {}".format(line, e))
        except ValueError as e:
            exit("Unable to process {} - {}".format(line, e))
    return res

if __name__ == "__main__":
    logfile = 'data/logfile.txt'
    # with open(logfile, 'r') as infile:
    #     arr = infile.readlines()
    #     lengths = [int(line.split(":")[1]) for line in arr[1:]]
    #     lengths.sort()

    # compute_stats(lengths)
    plot_distributions(logfile)
    # plot_ratio_rev_contrib()
    # find_longest_ts(logfile)