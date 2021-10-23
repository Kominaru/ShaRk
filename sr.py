import numpy as np
import os
import matplotlib.pyplot as plt
import math
from numpy.lib.function_base import average
from scipy.interpolate import make_interp_spline, BSpline
import random


class HitObject:
    def __init__(self, column, timestamp, lnend=0) -> None:
        self.column = column
        self.timestamp = timestamp
        self.isln = lnend > 0
        self.lnend = lnend


maps_folder = "./mapas/"


def obtainHitObjectArrayFromOsu(file):
    hitobjects = []
    l = file.readline()
    while "[HitObjects]" not in l:
        l = file.readline()

    while True:
        l = file.readline()
        if not l: break
        lineinfo = l.split(',')
        column = (int(lineinfo[0]) - 64) // 128
        timestamp = int(lineinfo[2])
        lnend = int(lineinfo[5].split(":")[0])
        hitobjects.append(HitObject(column, timestamp, lnend))

    return hitobjects


def obtainDensityCalculation(ho, bin_size):
    # TODO: Could consider np.histogram
    # https://numpy.org/doc/stable/reference/generated/numpy.histogram.html#numpy.histogram
    #
    # Example:
    # np.histogram([1, 2, 1], bins=[0, 1, 2, 3])
    # >> (array([0, 2, 1]), array([0, 1, 2, 3]))
    # First array is the histogram
    # Second is the histogram edges? Not too sure if you need it though

    v = np.zeros(int(math.ceil(ho[-1].timestamp - ho[0].timestamp) / bin_size))
    x = np.zeros(int(math.ceil(ho[-1].timestamp - ho[0].timestamp) / bin_size))
    d = 0
    i = 0
    b = 0
    while i in range(len(ho)):
        if ho[i].timestamp <= (ho[0].timestamp + (b + 1) * bin_size):
            d += 1
            i += 1
        else:
            x[b] = b * bin_size
            v[b] = d * (1000 / bin_size)
            b += 1
            d = 0
    plt.plot(x, v, color="blue")
    plt.show()
    return np.average(v)


def obtainDensityCalculation2(ho, bin_size):
    v = np.zeros(len(ho), dtype=int)
    # TODO: x not used
    x = np.zeros(len(ho), dtype=int)
    j = 0
    k = 0

    # TODO: lastt not used
    lastt = -1
    for i in range(len(ho)):
        # if ho[i].timestamp==lastt:
        #     v[i]=-1
        #     x[i]=-1
        #     continue
        # lastt=ho[i].timestamp
        d = 0
        while ho[j].timestamp < (ho[i].timestamp - bin_size / 2):
            j += 1

        while ho[k].timestamp < (ho[i].timestamp + bin_size / 2) and k < len(ho) - 1:
            k += 1

        v[i] = k - j

    return v


def obtainManipCalculation(ho, bin_size):
    v = np.zeros(len(ho))
    # TODO: x not used
    x = np.zeros(len(ho))
    j = 0
    k = 0
    for i in range(len(ho)):
        while ho[j].timestamp < (ho[i].timestamp - bin_size / 2):
            j += 1

        while ho[k].timestamp < (ho[i].timestamp + bin_size / 2) and k < len(ho) - 1:
            k += 1

        d = [1, 1, 1, 1]
        for h in range(j, k):
            d[ho[h].column] = d[ho[h].column] + 1

        l_manip = min(d[:2]) / max(d[:2]) / (1 + np.var(d[:2]))  # [0,1]Closer to 1-> more masheable
        r_manip = min(d[2:]) / max(d[2:]) / (1 + np.var(d[2:]))
        h_manip = min(sum(d[:2]), sum(d[2:])) / max(sum(d[:2]), sum(d[2:])) / (1 + np.var([sum(d[:2]), sum(d[2:])]))
        v[i] = np.average([l_manip, r_manip, h_manip])  # [0,1] Closer to 1 -> easier to mash
        # v[i]=(
        #     np.var(d[:2]) * (min(d[:2])/max(d[:2]))
        #    +np.var(d[2:]) * (min(d[2:])/max(d[2:]))
        #    +np.var([sum(d[:2]),sum(d[2:])]) * (min(sum(d[:2]),sum(d[2:]))/max(sum(d[:2]),sum(d[2:])))
        # )
    return v


# TODO: bin_size not used
def obtainMotionCalculation(ho, bin_size):
    v = np.zeros(len(ho))
    # TODO: x j k not used
    x = np.zeros(len(ho))
    j = 0
    k = 0

    supr_threshold = 35
    for i in range(len(ho)):
        # while ho[j].timestamp<(ho[i].timestamp-bin_size/2):
        #     j+=1

        # while ho[k].timestamp<(ho[i].timestamp+bin_size/2) and k<len(ho)-1:
        #     k+=1

        # m=0
        # before,after=False,False
        # if ho[i].timestamp!=ho[0].timestamp:
        #     print(ho[i].timestamp)
        #     print(ho[0].timestamp)
        #     n=0
        #     while ho[i-1-n].timestamp==ho[i].timestamp:
        #         n+=1
        #         print(i-1-n)
        #         print(ho[i-1-n].column,"",ho[i-1-n].timestamp)
        #     ch=ho[i].column
        #     c=ho[i-1-n].column
        #     csum=c+ch
        #     if c==ch:
        #         m+=1.5
        #     elif csum==5 or csum==1:
        #         m+=1
        #     else:
        #         m+=0.5
        #     before=True
        w = 0
        if ho[i].timestamp != ho[len(ho) - 1].timestamp:
            n = 0
            while ho[i + 1 + n].timestamp == ho[i].timestamp:
                n += 1
            distance = ho[i + 1 + n].timestamp - ho[i].timestamp
            nn = n
            while ho[i + 1 + nn].timestamp == ho[i + 1 + n].timestamp:
                ch = ho[i].column
                c = ho[i + 1 + nn].column
                csum = c + ch

                if c == ch:
                    w += 2
                else:
                    if distance < supr_threshold: distance = 2 * supr_threshold - distance
                    if csum == 5 or csum == 1:
                        w += 1.4
                    else:
                        w += 0.9
                nn += 1
                if (i + 1 + nn) >= len(ho): break

            v[i] = w * (100 / distance)
        else:
            v[i] = 0

    return v


# TODO: bin_size not used
def obtainInverseCalculation(ho, bin_size):
    v = np.ones(len(ho))

    # TODO: x j k not used
    x = np.zeros(len(ho))
    j = 0
    k = 0

    for i in range(len(ho)):
        if ho[i].isln and ho[i].timestamp != ho[-1].timestamp:
            n = 1
            while ho[i + n].column != ho[i].column:
                n += 1
                if i + n >= len(ho): break
            if i + n >= len(ho): break
            v[i] += 100 / (ho[i + n].timestamp - ho[i].lnend)
    return v


# TODO: bin_size not used
def obtainLNnessCalculation(ho, bin_size):
    v = np.ones(len(ho))

    # TODO: x j k not used
    x = np.zeros(len(ho))
    j = 0
    k = 0

    def s(x):
        return 1 / (1 + math.exp(9 - 0.1 * x))

    for i in range(len(ho)):
        if ho[i].isln:
            v[i] = s(ho[i].lnend - ho[i].timestamp)
    return v


# TODO: bin_size not used
def obtainReleaseCalculation(ho, bin_size):
    def s(x):
        return 1 / (1 + math.exp(-x))

    def f(x):
        # TODO: Return 1000 ?
        # If x is a primitive, e.g. int, float, x = 1000 will do nothing as it's pass by copy
        if x > 1000: x = 1000
        return s(0.1 * (x - 60)) + s(0.1 * (-x + 180)) - 1

    # TODO: x j not used
    v = np.zeros(len(ho))
    x = np.zeros(len(ho))
    j = 0
    m

    for i in range(len(ho)):
        if ho[i].isln:
            c = ho[i].column
            n = i
            while ho[n].timestamp < ho[i].lnend:
                n += 1
                if n >= len(ho): break
            if n >= len(ho): break
            t = 0
            cols = [0, 1, 2, 3]
            cols.remove(c)
            for col in cols:
                if c + col == 1 or c + col == 5:
                    a = 2
                else:
                    a = 1
                j = n
                while ho[j].column != col:
                    j -= 1
                    if j < 0: break
                if j < 0: break

                t += a * f(ho[i].lnend - ho[j].timestamp)

                if ho[j].lnend > ho[i].lnend:
                    t += a * f(ho[j].lnend - ho[i].lnend)
                else:
                    j = n + 1
                    if j >= len(ho): break
                    while ho[j].column != col:
                        j += 1
                        if j >= len(ho): break
                    if j >= len(ho): break
                    t += a * f(ho[j].timestamp - ho[i].lnend)
            v[i] = t
    return v


raw_alpha = 0.05
text = ["nanahoshi", "inai inai", "fortunate", "nostalgia", "levitation"]
dns_bin_size = 1000
mnp_bin_size = 1000
mtn_bin_size = 1000
w = 100
fig, ((dens, inverse), (manip, release), (motion, lnness), (rice_total, ln_total), (total, filler)) = plt.subplots(
    nrows=5, ncols=2, sharex=True)

i = .9
for m in os.listdir(maps_folder):
    if text != [] and not any([t in m.lower() for t in text]): continue
    with open(maps_folder + m, "r", encoding="utf8") as f:
        ho = obtainHitObjectArrayFromOsu(f)
        x = np.array([h.timestamp for h in ho])

        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)

        dns = obtainDensityCalculation2(ho, dns_bin_size)
        dns_roll = np.array([np.average(dns[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])

        dens.plot(x, dns, c=color, alpha=raw_alpha)
        dens.plot(x, dns_roll, label=m, c=color, linewidth=3)
        dens.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(dns_roll):0.2f}", horizontalalignment='left',
                  verticalalignment='center',
                  transform=dens.transAxes)
        dens.title.set_text("DNS - Density Component")
        mnp = obtainManipCalculation(ho, mnp_bin_size)
        mnp_roll = np.array([np.average(mnp[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        manip.plot(x, mnp, c=color, alpha=raw_alpha)
        manip.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(mnp_roll):0.2f}", horizontalalignment='left',
                   verticalalignment='center',
                   transform=manip.transAxes)
        manip.title.set_text("MSH - Mashability Component")
        manip.plot(x, mnp_roll, label=m, c=color, linewidth=3)
        manip.set_ylim(0.35, 0.85)
        mtn = obtainMotionCalculation(ho, mtn_bin_size)
        mtn_roll = np.array([np.average(mtn[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        motion.plot(x, mtn, c=color, alpha=raw_alpha)
        motion.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(mtn):0.2f}", horizontalalignment='left',
                    verticalalignment='center',
                    transform=motion.transAxes)
        motion.plot(x, mtn_roll, label=m, c=color, linewidth=3)
        motion.set_ylim(0, 3.5)
        motion.title.set_text("STR - Strain Component")

        inv = obtainInverseCalculation(ho, mtn_bin_size)
        inv_roll = np.array([np.average(inv[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        inverse.plot(x, inv, c=color, alpha=raw_alpha)
        inverse.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(inv):0.2f}", horizontalalignment='left',
                     verticalalignment='center',
                     transform=inverse.transAxes)
        inverse.plot(x, inv_roll, label=m, c=color, linewidth=3)
        inverse.title.set_text("LN-INV - LN Inverse Component")

        rel = obtainReleaseCalculation(ho, mtn_bin_size)
        rel_roll = np.array([np.average(rel[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        release.plot(x, rel, c=color, alpha=raw_alpha)
        release.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(rel):0.2f}", horizontalalignment='left',
                     verticalalignment='center',
                     transform=release.transAxes)
        release.plot(x, rel_roll, label=m, c=color, linewidth=3)
        release.title.set_text("LN-REL - LN Release Component")

        lns = obtainLNnessCalculation(ho, mtn_bin_size)
        lns_roll = np.array([np.average(lns[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        lnness.plot(x, lns, c=color, alpha=raw_alpha)
        lnness.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(lns):0.2f}", horizontalalignment='left',
                    verticalalignment='center',
                    transform=lnness.transAxes)
        lnness.plot(x, lns_roll, label=m, c=color, linewidth=3)
        lnness.title.set_text("LN-LNS - LN \"LNness\" Component")

        lnness.set_ylim(.25, 1)

        lnttl_raw = np.power((inv * rel), lns)
        lnttl = np.power((inv_roll * rel_roll), lns_roll)
        lnttl_roll = np.array([np.average(lnttl[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        ln_total.plot(x, lnttl_raw, c=color, alpha=raw_alpha)
        ln_total.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(lnttl):0.2f}", horizontalalignment='left',
                      verticalalignment='center',
                      transform=ln_total.transAxes)
        ln_total.plot(x, lnttl_roll, label=m, c=color, linewidth=3)
        ln_total.set_ylim(0, 8)
        ln_total.title.set_text("LN Total (INV*REL)^LNS")

        ricettl_raw = (dns / mnp) * mtn
        ricettl = (dns_roll / mnp_roll) * (mtn_roll)
        ricettl_roll = np.array(
            [np.average(ricettl[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        rice_total.plot(x, ricettl_raw, c=color, alpha=raw_alpha)
        rice_total.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(ricettl):0.2f}", horizontalalignment='left',
                        verticalalignment='center',
                        transform=rice_total.transAxes)
        rice_total.plot(x, ricettl_roll, label=m, c=color, linewidth=3)
        rice_total.set_ylim(0, 100)
        rice_total.title.set_text("RICE Total (DNS/MSH)*STR")

        ttl_raw = (dns / mnp) * mtn * np.power((inv * rel), lns)
        ttl = (dns_roll / mnp_roll) * (mtn_roll) * np.power((inv_roll * rel_roll), lns_roll)
        ttl_roll = np.array([np.average(ttl[max(0, i - w // 2):min(len(ho), i + w // 2)]) for i in range(len(ho))])
        total.plot(x, ttl_raw, c=color, alpha=raw_alpha)
        total.text(0.8, i, s=f"{m[:12] + '...'}Avg. diff= {np.average(ttl):0.2f}", horizontalalignment='left',
                   verticalalignment='center',
                   transform=total.transAxes)
        total.plot(x, ttl_roll, label=m, c=color, linewidth=3)
        total.set_ylim(0, 300)
        total.title.set_text("Total (DNS/MSH)*STR*(INV*REL)^LNS")

        i -= 0.1

dens.legend()
plt.show()
