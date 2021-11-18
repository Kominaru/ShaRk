import numpy as np
import math

###############################################################################
# Obtains the rhythm calculation for each note in the map by counting the
# amount of notes around the note in a timing window of size bin_size
###############################################################################
bin_size = 1000

#TO-DO: Make the window non-rigid by weighting over a bell curve over (-2,2) instead

def gaussian(x):
    return math.exp(-(x**2)/(2))

bind_500 = lambda x: max(min(x,500),-500)

def chord_suppression(x):
    grace_threshold=30
    slope=+0.2
    x=bind_500(x)
    return 1 / (1 + math.exp(grace_threshold*slope-slope*x))

def weighted_avg_and_std(values, weights):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))

def obtainRhythmCalculation(ho):
    rhythm = np.ones(len(ho))
    wl = 0  # Current index of the note that first enters in the window
    wr = 0  # Same but for last

    for i in range(len(ho)):
        r=0
        # Find the new first note that is inside the window
        while ho[wl].timestamp < (ho[i].timestamp-bin_size/2):
            wl += 1

        # Fin the new last note that is inside the window
        while ho[wr].timestamp < (ho[i].timestamp+bin_size/2) and wr < len(ho)-1:
            wr += 1

        if wr-wl>0:

            #Raw distances between consecutive notes
            distances=np.zeros(wr-wl)
            #Gaussian weights assigned depending on distance to i, the center of the window (basically to smooth the calculations like in Density and Manip models)
            weights=np.zeros(wr-wl)

            #We always use the closest note to i as the note to calculate the weight with (gaussian(((ho[j+1]... vs. gaussian(((ho[j]...)
            for j in range(wl,i):
                distances[j-wl]=ho[j+1].timestamp-ho[j].timestamp
                weights[j-wl]=gaussian(((ho[j+1].timestamp-ho[i].timestamp)/(bin_size/2))*3)*chord_suppression(ho[j+1].timestamp-ho[j].timestamp)
            for j in range(i,wr):
                distances[j-wl]=ho[j+1].timestamp-ho[j].timestamp
                weights[j-wl]=gaussian(((ho[j].timestamp-ho[i].timestamp)/(bin_size/2))*3)*chord_suppression(ho[j+1].timestamp-ho[j].timestamp)
                
            #Compute the weighted avg and std deviation, rhythm difficulty for that note is stdev/avg. Perhaps this metric is not correct and favors higher BPM /lower BPM/faster maps?
            norm_avg,norm_stdev=weighted_avg_and_std(distances,weights)
            rhythm[i] += norm_stdev/(1+norm_avg)


    return rhythm
