import numpy as np
import math

jack_w = 3
onehand_w = 1.0
twohand_w = 0.8

bind_500 = lambda x: max(min(x,500),-500)


def s(x):
    grace_threshold = 60
    slope = 0.1
    x = bind_500(x)

    return 1 / (1 + math.exp(grace_threshold*slope - slope*x))


def oh_stream_supr_f(x):
    grace_threshold = 30
    slope = -0.2
    x=bind_500(x)

    return 1 / (1 + math.exp(grace_threshold*slope - slope*x))


def oh_double_supr_f(x):
    grace_threshold = 0
    slope = -0.2
    x=bind_500(x)

    return 1 / (1 + math.exp(grace_threshold*slope - slope*x))


def th_stream_supr_f(x):
    grace_threshold = 30 
    slope = -0.2
    x=bind_500(x)

    return 1 / (1 + math.exp(grace_threshold*slope - slope*x))


def jack_self_supr_f(x):
    grace_threshold = 30 
    slope = -0.2
    x = bind_500(x)

    return 1 / (1 + math.exp(grace_threshold*slope - slope*x))


###############################################################################
# Obtains the strain of hitting each consecutive note pair based on the type of
# motion it requires (same hand but different column, different hand, jack)
###############################################################################


# TO-DO: Consider separately all 4 columns for each note? Currently it's buggy cause if one note isn't a jack then it gets supressed a lot by the distance thing

def obtainStrainCalculation(ho):
    strain = np.zeros(len(ho))

    for i in range(len(ho)):
        # Total strain difficulty of the note
        strain[i] = 0  

        # Last note doesn't get assigned any value
        if ho[i].timestamp != ho[len(ho) - 1].timestamp:
            j = 0

            # Find the next note after the current one
            for c in [ 0, 1, 2, 3 ]:
                j = i

                # Other column in the same hand
                c_oh_i = 2*(ho[i].column//2) + (ho[i].column + 1) % 2

                # Other column in the same hand
                c_oh_j = 2*(c//2) + (c + 1) % 2

                # Find j
                while (ho[j].timestamp == ho[i].timestamp) or (c != ho[j].column):
                    j += 1
                    if j >= len(ho):
                        break

                if j >= len(ho): 
                    continue

                
                distance = ho[j].timestamp - ho[i].timestamp
                csum = ho[j].column + ho[i].column

                #################################
                ############ JACKS ##############
                #################################

                if c == ho[i].column:
                    # Different column in the same hand

                    # List index pointer for iteration
                    k = i

                    # Notes that could make the jack [i n2] and [j n1] (j is the next note in c after i)
                    n2 = -1
                    n1 = -1   
                    
                    # While we don't obtain both notes or run out of notes to check, go backward through the HitObjects list
                    while (not k < 0) and (n1 == -1):
                        # If we find a note in the desired column, "roll" the elements of the "queue" adding the new found note
                        if ho[k].column == c_oh_i:
                            n1 = n2
                            n2 = k

                        k -= 1

                    # If we ran out of notes before i and couldn't find two 
                    if (k < 0) and (n1 != 1): 
                        # Start looking for the missing notes after i this time
                        k = i + 1
                        
                        # While we don't obtain both this time or run out of notes to check, go forward through the HitObjects list
                        while (k < len(ho)) and ((n1 == -1) or (n2 == -1)):
                            # If we find a note in the desired column, update n2 and n1
                            if ho[k].column == c_oh_i:
                                if n2 == -1: 
                                    # If we had already found one note in the previous while, lock n2
                                    n2 = n1

                                n1 = k

                            k += 1

                    # If we didn't have enough notes, just don't supress for jacks
                    if (n2 == -1) or (n1 == -1): 
                        supress = 1 
                    # Else, start iterating forward (find next noteS after n1 in c_oh_i)
                    else:
                        k = n1 + 1
                        while k < len(ho):
                            if ho[k].column == c_oh_i:
                                d1 = abs(ho[i].timestamp - ho[n2].timestamp) + abs(ho[j].timestamp - ho[n1].timestamp)  # Old pair distance
                                d2 = abs(ho[i].timestamp - ho[n1].timestamp) + abs(ho[j].timestamp - ho[k].timestamp)   # New pair distance
                                
                                # If it increased, curent pair is better
                                if d2 > d1: 
                                    break
                                # Otherwise move the currrent pair to the new found one
                                else:
                                    n2 = n1
                                    n1 = k

                            k += 1

                        supress = 0.5**((1 - s(abs(ho[i].timestamp - ho[n2].timestamp)))*(1 - s(abs(ho[j].timestamp - ho[n1].timestamp))))

                    strain[i] += jack_w*(100/distance)*supress

                # Otherwise, supress based on how gracey it is
                else:
                    k = j
                    while (ho[j].timestamp == ho[k].timestamp) or (c != ho[k].column):
                        k -= 1
                        if k < 0: 
                            break

                    # Jack suppression 
                    jack_supr = 1 if (k < 0) else s(ho[i].timestamp - ho[k].timestamp)

                    # Grace suppression
                    grace_supr = s(ho[j].timestamp - ho[i].timestamp) 
                    
                    k = j
                    while c_oh_i != ho[k].column:
                        k -= 1
                        if k < 0:
                            break

                    oh_stream_supr = 1 if k < 0 else oh_stream_supr_f(ho[j].timestamp - ho[k].timestamp)
                    oh_double_supr = 1 if k < 0 else oh_double_supr_f(ho[k].timestamp - ho[i].timestamp)
                    
                    k = j
                    while c_oh_j != ho[k].column:
                        k -= 1
                        if k < 0:
                            break

                    th_stream_supr = 1 if (k < 0) else th_stream_supr_f(ho[j].timestamp - ho[k].timestamp)

                    k = i
                    while (ho[i].column != ho[k].column) or (k == i):
                        k += 1
                        if k >= len(ho):
                            break

                    jack_self_supr = 1 if (k >= len(ho)) else jack_self_supr_f(ho[j].timestamp - ho[k].timestamp)
                    
                    # if ho[i].timestamp>81500 and ho[i].timestamp<82500:
                        # print("========================",c_oh_i,c_oh_j)
                        # print(f"Timestamp(i): {ho[i].timestamp}$f.2 | Column(i): {ho[i].column} || Timestamp(j): {ho[j].timestamp} | Column(j): {ho[j].column}")
                        # print(f"Base Strain: {(100/distance):.2f} | Grace suppresion: {grace_supr:.2f} | Jack supression: {jack_supr:.2f} | Self jack supression: {jack_self_supr:.2f} | Oh_othercolumn suppresion: {min(oh_stream_supr+oh_double_supr,1):.2f} | Th_othercolumn suppresion: {th_stream_supr:.2f}")


                    if (csum == 5) or (csum == 1):
                        strain[i] += onehand_w*(100/distance)*jack_supr*grace_supr*jack_self_supr
                        # if ho[i].timestamp>81500 and ho[i].timestamp<82500:
                            # print(f"Total: {(100/distance)*jack_supr*grace_supr*jack_self_supr:.2f}")
                                # Different hand
                    else:
                        # if (oh_stream_supr+oh_double_supr)>1: print(ho[i].timestamp, ho[i].column, ho[j].column, (oh_stream_supr+oh_double_supr), oh_stream_supr, oh_double_supr); input()
                        strain[i] += twohand_w*(100/distance)*jack_supr*grace_supr*(min(oh_stream_supr+oh_double_supr, 1))*th_stream_supr*jack_self_supr
                        # if ho[i].timestamp>81500 and ho[i].timestamp<82500:
                            # print(f"Total: {(100/distance)*jack_supr*grace_supr*(min(oh_stream_supr+oh_double_supr,1))*th_stream_supr*jack_self_supr:.2f}")
    return strain
