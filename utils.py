import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller


def adf(ts, window=7, disp=False):
    # Determing rolling statistics
    rolmean = pd.Series.rolling(ts, window=window, center=False).mean()
    rolstd = pd.Series.rolling(ts, window=window, center=False).std()

    #Plot rolling statistics:
    orig = plt.plot(ts, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    plt.close()
    # Calculate ADF factors
    adftest = adfuller(ts, autolag='AIC')
    if disp:
        adfoutput = pd.Series(adftest[0:4], index=['Test Statistic', 'p-value', '# of Lags Used',
                                               'Number of Observations Used'])
        for key,value in adftest[4].items():
            adfoutput['Critical Value (%s)' % key] = value

    return adftest


def is_stationary(ts):
    adftest = adf(ts)
    return adftest[1] < 0.5 and any([v > adftest[0] for k, v in adftest[4].items()])


def RMSE(predicted, actual):
    mse = (predicted - actual)**2
    rmse = np.sqrt(mse.sum()/mse.count())
    return rmse