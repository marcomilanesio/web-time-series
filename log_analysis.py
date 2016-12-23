import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from scipy.stats.kde import gaussian_kde


def compute_stats(lengths):
    print("Min: {}".format(np.min(lengths)))
    print("Max: {}".format(np.max(lengths)))
    print("Mean: {}".format(np.mean(lengths)))
    print("Std: {}".format(np.std(lengths)))
    print("Median (50-tile): {}".format(np.percentile(lengths, 50)))   # median.
    print("95-tile: {}".format(np.percentile(lengths, 95)))
    print("zero-length: {}".format(lengths.count(0)))
    print("95-length: {}".format(lengths.count(np.percentile(lengths, 95))))
    print("max-length: {}".format(lengths.count(np.max(lengths))))


def plot_distributions(lengths):
    figname = './results/distributions.pdf'
    mu = np.mean(lengths)
    std = np.std(lengths)
    cdf = stats.norm.cdf(lengths, mu, std)

    kde = gaussian_kde(lengths)
    dist_space = np.linspace(min(lengths), max(lengths), 100)

    fig, ax1 = plt.subplots()
    pdf_line = ax1.plot(dist_space, kde(dist_space), 'b+', label="pdf")
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
    print(np.min(ratios), np.max(ratios), np.mean(ratios), np.std(ratios), np.median(ratios), np.percentile(ratios, 95))
    ratios.sort()
    mu = np.mean(ratios)
    std = np.std(ratios)
    cdf = stats.norm.cdf(ratios, mu, std)
    fig = plt.figure()
    plt.plot(ratios, cdf, 'r-', label="ratio")
    plt.savefig('results/ratio_rev_contrib.pdf')
    plt.close()

if __name__ == "__main__":
    # logfile = 'data/logfile.txt'
    # with open(logfile, 'r') as infile:
    #     arr = infile.readlines()
    #     lengths = [int(line.split(":")[1]) for line in arr[1:]]
    #     lengths.sort()

    # compute_stats(lengths)
    # plot_distributions(lengths)
    plot_ratio_rev_contrib()