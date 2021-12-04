import numpy as np
import math


def s90(x):
    return 1 / (1 + math.exp(9-0.1*x))

# Sigmoidal
def s(x):
    if x >  100: x =  100
    if x < -100: x = -100
    return 1 / (1 + math.exp(-x))


# Sigmoidal-based function that peaks at around 120 and descends on both sites
def f(x):
    if x > 1000:
        x = 1000

    return s(0.1*(x - 60)) + s(0.1*(-x + 180)) - 1


##########################################
def jack_next(b_next_press, a_next_press):
    d = a_next_press - b_next_press
    if d < -500: 
        d = -500

    return 1/(1+math.exp(-0.125*(d - 40)))


def stream_next(b_next_press, i_release):
    d = b_next_press - i_release

    return s(-6 + .1*d) + s(20 - .1*d) - 1


def stream_next_supressor(b_next_press, i_release):
    d = b_next_press - i_release
    if d < -500: 
        d = -500
    
    return 1/(1 + math.exp(-0.125*(abs(d) - 40)))


def stream_prev1(b_prev_press, i_release):
    d = i_release - b_prev_press

    return s(-6 + .1*d) + s(20 - .1*d) - 1


def stream_prev2(b_prev_release, i_press):
    d = i_press - b_prev_release

    return s(-6 + .1*abs(d)) + s(20 - .1*abs(d)) - 1


def release_prev(b_prev_release, i_release):
    d = i_release - b_prev_release

    return s(-6 + .1*abs(d)) + s(20 - .1*abs(d)) - 1


def release_prev_supr(b_prev_release, i_release):
    d = i_release - b_prev_release
    if d < -500:
        d = -500

    return 1/(1 + math.exp(-0.125*(abs(d) - 60)))


def release_next(b_next_release, a_next_press):
    d = a_next_press - b_next_release
    if d < -500:
        d = -500

    return 1/(1 + math.exp(-0.125*(d - 40)))


###############################################################################
#   Obtain the release/timing difficulty of each LN based on how the timings of
#   the ln ends and notes surrounding the release (one for each column)
###############################################################################

# TO-DO: I suspect the algorithm is not working properly (check )

onehand_w = 2.5
twohand_w = 1.2

def obtainReleaseCalculation(ho):
    v = np.zeros(len(ho))

    for i in range(len(ho)):
        if ho[i].isln:
            c = ho[i].column
            n = i

           
            # Obtain the index of the note that is at i's ln end or the nearest after it
            while ho[n].timestamp < ho[i].lnend:
                n += 1
                if n >= len(ho):
                    break

            if n >= len(ho):
                continue

            r = 0  # Release difficulty counter

            # Find the a_next note in the same column
            a_next = n 
            while ho[a_next].column != c:
                a_next += 1
                if a_next >= len(ho):
                     break

            if a_next >= len(ho):
                continue

            cols = [ 0, 1, 2, 3 ]
            cols.remove(c)

            # For all the columns that aren't the note's one

            r_prev = 0
            r_next = 0
            ln_stream = 0

            for col in cols:
                # Choose weight based on column combination
                a = onehand_w if (c + col == 1) or (c + col == 5) else twohand_w

                # Find the previous closest note in that column...
                j = n
                while ho[j].column != col or j == n:
                    j -= 1
                    if j < 0:
                        break

                if j < 0:
                    continue
                
                # Find the following closest note in that column...
                k = n
                while ho[k].column != col:
                    k += 1
                    if k >= len(ho):
                        break

                if k >= len(ho):
                    continue
                
                rp  = release_prev(ho[j].lnend, ho[i].lnend)
                rps = release_prev_supr(ho[j].lnend, ho[i].lnend)
                sn  = stream_next(ho[k].timestamp, ho[i].lnend)
                sns = stream_next_supressor(ho[k].timestamp, ho[i].lnend)
                rn  = release_next(ho[j].lnend, ho[a_next].timestamp)
                sp1 = stream_prev1(ho[j].timestamp, ho[i].lnend)
                sp2 = stream_prev2(ho[j].lnend, ho[i].timestamp)
                jn  = jack_next(ho[k].timestamp, ho[a_next].timestamp)

                ln_stream *= sns

                r_prev += a*rp*sns*rn*sp1*sp2
                r_next += a*sn*jn*rps

                # if ho[i].timestamp>24000 and ho[i].timestamp<27000 and (r_prev+r_next)>.3:
                #     print("="*20)
                #     print(f"Timestamp {ho[i].timestamp} | Col(i): {ho[i].column} | Col(j,k): {ho[j].column}")
                #     print(f"Release_Prev: {rp} | Release_Prev_Supression: {rps}")
                #     print(f"Stream_Next: {sn} | Stream_Next_Supression: {sns}")
                #     print(f"Release_next: {rn}")
                #     print(f"Stream_prev1: {sp1}")
                #     print(f"Stream_prev2: {sp2}")
                #     print(f"Jack_Next: {jn}")
                #     print(f"Difficulty of Prev: {a*rp*sns*rn*sp1*sp2} | Difficulty of Next: {a*sn*jn}")

            #     # ...and add the difficulty to the counter based on timing difference
            #     if ho[j].isln:
            #         # Notice the abs to support both cases
            #         r += a*f(abs(ho[i].lnend-ho[j].lnend))*s90(abs(ho[i].timestamp-ho[j].lnend))
            #         if ho[i].timestamp==58110: print(ho[i].timestamp, ho[j].column, r)
            #     else:
            #         r += a*f(min(ho[i].lnend-ho[j].timestamp,1000))
    
            #     # ... and add it to the counter
            #     r += a*f(ho[j].timestamp-ho[i].lnend)*s90(max(min(ho[a_next].timestamp-ho[j].timestamp,1000),-1000))
            # if ho[i].timestamp==58110: print(ho[i].timestamp, ho[i].column, r)
            # if ho[i].timestamp>24000 and ho[i].timestamp<27000 and (r_prev+r_next*ln_stream)>.3:
            #         print("="*20)
            #         print(f"Timestamp {ho[i].timestamp} | Col(i): {ho[i].column} | R: {r_prev+r_next*ln_stream}")
            v[i] = r_prev + r_next*ln_stream

    return v
