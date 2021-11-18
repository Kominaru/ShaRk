import numpy as np
import math

###############################################################################
# Obtains the manipulabilty of each note based on each surroundings. If the
# amount of notes between each hand's columns and between hands is balanced,
# then the patterning is highly manipulable
###############################################################################
bin_size = 1000

def gaussian(x):
    return math.exp(-(x**2)/(2))

def obtainManipCalculation(ho):

    n_ho=len(ho)
    manip = np.zeros(n_ho)
    col_counts = np.zeros(4)
    wl = 0  # Current index of the note that first enters in the window
    for i in range(n_ho):

        t = ho[i].timestamp
        # Find the new first note that is inside the window
        while ho[wl].timestamp < (t-bin_size/2):
            wl += 1

        col_counts[:]=0

        wr=wl
        # Fin the new last note that is inside the window, count notes per column
        
        while ho[wr].timestamp <= (t+bin_size/2) and wr < n_ho:
            col_counts[ho[wr].column] += gaussian(((ho[wr].timestamp-t)/(bin_size/2))*3)
            wr += 1
            if wr>=n_ho:
                break


        hand_counts=col_counts[1::2]+col_counts[0::2]
        l_hand=col_counts[:2]
        r_hand=col_counts[2:]

        def var(a,b):
            return ((a-b)**2)/((a+b)/2)

        
        # How easy is to manipulate the patterning in the left hand
        if ho[i].column in [0,1]:
            m=np.amin(np.amax(l_hand)-2*np.sqrt(l_hand*(np.amax(l_hand)-l_hand)))/np.amax(l_hand)
        # How easy is to manipulate the patterning in the right hand
        else:
            m=np.amin(np.amax(r_hand)-2*np.sqrt(r_hand*(np.amax(r_hand)-r_hand)))/np.amax(r_hand)
        
        manip[i] = (1/(2-m))**2

    return manip
