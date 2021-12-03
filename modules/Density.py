import numpy as np
import math

###############################################################################
# Obtains the density calculation for each note in the map by counting the
# amount of notes around the note in a timing window of size bin_size
###############################################################################
bin_size = 1000

#TO-DO: Make the window non-rigid by weighting over a bell curve over (-2,2) instead


def obtainDensityCalculation(ho):
    gaussian = lambda x: math.exp(-(x**2)/(2))
    density = np.zeros(len(ho))
    
    wl = 0  # Current index of the note that first enters in the window
    wr = 0  # Same but for last

    for i in range(len(ho)):
        d = 0

        # Find the new first note that is inside the window
        while ho[wl].timestamp < (ho[i].timestamp - bin_size/2):
            wl += 1

        # Find the new last note that is inside the window
        while ho[wr].timestamp < (ho[i].timestamp + bin_size/2) and wr < len(ho) - 1:
            wr += 1

        for j in range(wl,wr+1):
            distance = ((ho[j].timestamp-ho[i].timestamp)/(bin_size/2))*3
            d += gaussian(distance)

        # The note count is simply the index difference
        density[i] = d

    return density
