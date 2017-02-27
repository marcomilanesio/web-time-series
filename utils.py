import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
import statsmodels.tsa.api as smt
import seaborn as sns
sns.set(style='ticks', context='talk')


def plot_ts(ts, title, fname):
    rolmean = pd.Series.rolling(ts, window=12, center=False).mean()
    rolstd = pd.Series.rolling(ts, window=12, center=False).std()
    orig = plt.plot(ts, color='blue', label='Original')
    mean = plt.plot(rolmean, linestyle='dashed', color='red', label='Rolling Mean')
    std = plt.plot(rolstd, linestyle='dotted', color='black', label='Rolling Std')
    plt.ylim(ymax=100)
    plt.legend(loc='best')
    plt.title(title)
    # plt.show(block=False)
    plt.savefig(fname)
    plt.close()


def adf(ts, fname=None, disp=None):
    if fname:
        plot_ts(ts, title='Rolling Mean & Standard Deviation', fname=fname)
    # Calculate ADF factors
    adftest = adfuller(ts, autolag='AIC')
    if disp:
        adfoutput = pd.Series(adftest[0:4], index=['Test Statistic', 'p-value', '# of Lags Used',
                                                   'Number of Observations Used'])
        for key,value in adftest[4].items():
            adfoutput['Critical Value (%s)' % key] = value
        print(adfoutput)
    return adftest


def is_stationary(ts):
    adftest = adf(ts)
    return adftest[1] < 0.5 and any([v > adftest[0] for k, v in adftest[4].items()])


def RMSE(predicted, actual):
    mse = (predicted - actual)**2
    rmse = np.sqrt(mse.sum()/mse.count())
    return rmse


def differentiate(ts):
    return ts.diff().dropna()


def log_transform(ts):
    return np.log(ts)


def find_acf_pacf(ts, nlags=12, fname=None):
    lag_acf = acf(ts, nlags=nlags)
    lag_pacf = pacf(ts, nlags=nlags, method='ols')
    if fname:
        #Plot ACF:
        plt.subplot(121)
        plt.plot(lag_acf)
        plt.axhline(y=0, linestyle='--', color='gray')
        plt.axhline(y=-1.96/np.sqrt(len(ts)), linestyle='--',color='gray')
        plt.axhline(y=1.96/np.sqrt(len(ts)), linestyle='--',color='gray')
        plt.title('Autocorrelation Function')
        #Plot PACF:
        plt.subplot(122)
        plt.plot(lag_pacf)
        plt.axhline(y=0, linestyle='--', color='gray')
        plt.axhline(y=-1.96/np.sqrt(len(ts)), linestyle='--',color='gray')
        plt.axhline(y=1.96/np.sqrt(len(ts)), linestyle='--',color='gray')
        plt.title('Partial Autocorrelation Function')
        plt.tight_layout()
        plt.savefig(fname)
        plt.close()
    return lag_acf, lag_pacf


if __name__ == "__main__":
    from mongodb_client import DB
    c = DB()
    id_ = '585bbc0b951c421d18beaf53'
    doc = c.get_document(id_)
    df = doc['df']
    ts = df['num_rev']
    plot_ts(ts, 'Charles_Bukowski:num_rev', './test.pdf')
