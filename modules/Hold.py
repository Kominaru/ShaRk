import numpy as np
import math


###############################################################################
# Obtains for each note the additional "strain" created by having an LN pressed
# in the other finger of the same hand
###############################################################################


def obtainHoldCalculation(ho):
    s = lambda x: 1 / (1 + math.exp(9 - 0.1*x))
    v = np.ones(len(ho))

    for i in range(len(ho)):
        c = (ho[i].column+1) % 2 if ho[i].column in [0,1] else (ho[i].column-1) % 2 + 2
        j = i

        while ho[j].column != c:
            j -= 1
            if j < 0:
                break

        if j < 0:
            continue

        if ho[j].lnend > ho[i].timestamp:
            d1 = ho[j].lnend - ho[i].timestamp
            d2 = ho[i].timestamp - ho[j].timestamp

            v[i] += s(d1)*s(d2)

    return v
