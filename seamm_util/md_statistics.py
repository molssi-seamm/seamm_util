# -*- coding: utf-8 -*-

"""Helpful routine using the underlying Python functions
in 'statistics' and 'statsmodels' to handle common needs
in molecular modeling
"""

import logging
import random
import statistics
import statsmodels.tsa.stattools as stattools

logger = logging.getLogger(__name__)


def analyze_autocorrelation(
    y, interval=1, nlags=64, method='zr', use_confidence=False
):
    """Find the statistical inefficiency, correlation time and other useful
    parameters given the time sequence of values 'y'.

    This function implements two approaches, 'zr' and 'cspsd' corresponding to
    the two papers (using the initials as the method name):

    zr: Zięba, A.; Ramza, P. Standard Deviation of the Mean of Autocorrelated
    Observations Estimated with the Use of the Autocorrelation Function
    Estimated From the Data. Metrology and Measurement Systems 2011, 18 (4),
    3–14.

    cspsd: Chodera, J. D.; Swope, W. C.; Pitera, J. W.; Seok, C.; Dill,
    K. A. Use of the Weighted Histogram Analysis Method for the Analysis of
    Simulated and Parallel Tempering Simulations. J. Chem. Theory Comput. 2006,
    3 (1), 26–41.

    Args:
        y ([float]): the time sequence to analyze
        interval (float): the time interval between values, defaults to 1
        nlags (int): the number of lags to start with
        method (str): the approach to use, 'zr' or 'cspsd'. Defaults to 'zr'

    Returns:
        dict(
            'n': (int) number of values in y
            'n_effective': (int) effective number of uncorrelated values
            'n_c': (int) the first zero crossing in the ACF
            'n_tau': (int) number of intervals in the correlation time
            'tau': (float) the correlation time if <interval> is correct
            'inefficiency': (float) the statistical inefficiency
            'acf': ([float]) the autocorrelation function
            'confidence_interval': [(float, float)] the 95% confidence interval

    The input parameter <nlags> is solely for performance. Since calculating
    the ACF is expensive (O(N^2)) and often the correlation time is short, at
    least if the trajectory is sampled reasonably, this function starts with a
    small number of lags, and doubles the number repeatedly if it does not find
    the zero crossing it expects.
    """

    # Find the autocorrelation time...
    n = len(y)

    logger.debug('analyze_autocorrelation for a vector of length {}'.format(n))

    if nlags >= n:
        nlags = n - 1

    while True:
        logger.debug('   nlags = {}'.format(nlags))

        acf, confidence = stattools.acf(
            y, nlags=nlags, alpha=0.05, fft=nlags > 16, unbiased=False
        )

        # remove the first items, which are 1 by definition
        acf = acf[1:]
        confidence = confidence[1:]

        # Find the last lag that is > 0
        sum_acf = 0.0
        n_c = 0
        if use_confidence:
            for lower, upper in confidence:
                delta = acf[n_c] - lower
                value = lower + delta * 3 / 4
                if nlags == n - 1:
                    print(value)
                if value < 0:
                    break
                sum_acf += acf[n_c]
                n_c += 1
        else:
            for value in acf:
                if nlags == n - 1:
                    print(value)
                if value < 0:
                    break
                sum_acf += value
                n_c += 1

        # If we found n_c, go on. Otherwise double the lags
        if value < 0:
            break
        else:
            if nlags == n - 1:
                raise RuntimeError(
                    'analyze_autocorrelation: Serious error! '
                    'Did not find negative autocorrelation value.'
                )
            nlags *= 2
            if nlags >= n:
                nlags = n - 1

    logger.debug('   n_c = {}'.format(n_c))

    if method == 'zr':
        # Use the approach of Zięba and Ramza
        n_eff = (n - 2 * n_c - 1 + n_c * (n_c + 1) / n) / (1 + 2 * sum_acf)
        inefficiency = n / n_eff
        n_tau = (inefficiency - 1) / 2
    else:
        # Use the approach of Chodera, Swope, Pitera, Seok and Dill
        n_tau = 0.0
        for t in range(0, n_c):
            n_tau += (1 - (t + 1) / n) * acf[t]

        inefficiency = 1 + 2 * n_tau
        n_eff = n / inefficiency

    tau = n_tau * interval

    result = {
        'n': n,
        'n_effective': n_eff,
        'n_c': n_c,
        'n_tau': n_tau,
        'tau': tau,
        'inefficiency': inefficiency,
        'acf': acf,
        'confidence_interval': confidence
    }

    return result


def ar1(n=1000, a=10.0, b=0.2, sigma=0.5, seed=None):
    """Generate an AR(1) series of length n
    """
    r = random.Random()
    r.seed(seed)

    y0 = a / (1 - b)
    y = [0.0] * n
    y[0] = a + b * y0 + sigma * (r.random() - 0.5)
    for i in range(1, n):
        y[i] = a + b * y[i - 1] + sigma * (r.random() - 0.5)

    return y


if __name__ == "__main__":
    print('in end section')
    import time

    print()

    a = 10.0
    b = 0.9
    for n in (15, 60, 240, 512, 1024, 2048, 10000, 100000):
        y = ar1(n, a=a, b=b, seed=52)
        t0 = time.time()
        r1 = analyze_autocorrelation(y, method='zr', nlags=4)
        t1 = time.time()
        r2 = analyze_autocorrelation(
            y, method='zr', nlags=4, use_confidence=True
        )
        t2 = time.time()

        print('{:>20s} = {:7.3f} {:7.3f}'.format('time', t1 - t0, t2 - t1))
        print(
            '{:>20s} = {} {}'.format('nlags', len(r1['acf']), len(r2['acf']))
        )
        for key in r1:
            if key not in ['acf', 'confidence_interval']:
                print(
                    '{:>20s} = {:7.1f} {:7.1f}'.format(key, r1[key], r2[key])
                )

        ave = statistics.mean(y)
        stdev = statistics.stdev(y)
        print('                mean = {:9.3f}'.format(a / (1 - b)))
        print('                 ave = {:9.3f}'.format(ave))
        print('               stdev = {:9.3f}'.format(stdev))
        print()
