import numpy as np
import os
import matplotlib.pyplot as plt
from numpy.lib.function_base import average
import random
import csv
from utils.osu_api import extractBeatmapIds, getOsuFile

from utils.parser import *

from time import time


plots=False #Whether to plot stuff 
wcsv=True  #Whether to write results into csv




# CSV header row
header = [ 'Beatmap ID', 'Collection Name', 'Chart Name', 'Density', 'Manipulability', 'Strain', 'RICE TOTAL', 'Inverse', 'Release', 'Hold', 'LNNess', 'LN TOTAL', 'GLOBAL', 'DT GLOBAL' ]


counter=1
i = .9
t = time()

maps_folder  = './mapas/'
colls_folder = './collections/'

os.makedirs('csvs', exist_ok=True)
os.makedirs('cached_maps', exist_ok=True)

if wcsv: 
    csv_file = open('./CSVS/ALL.csv', 'w', encoding='UTF8', newline='')
    global_writer = csv.writer(csv_file)
    global_writer.writerow(header)

mode = 'ranked'

if mode == 'collections':
    # Identify all collections in collections folder
    for coll in os.listdir(colls_folder):
        i = .9

        fig, ((dens, inverse), (manip, release), (strain, lnness), (rice_total, hold), (total,  ln_total)) = plt.subplots(nrows=5, ncols=2, sharex=True)
        
        coll_name = coll.split('.')[0]
        with open(colls_folder + coll, 'r', encoding='utf8', errors='ignore') as f: 
            
            # Find all beatmap IDs in the file
            beatmap_list = extractBeatmapIds(f.read())

            # Prepare CSV collection
            if wcsv: 
                csv_file = open(f'./csvs/{coll_name}.csv', 'w', encoding='UTF8', newline='')
                writer = csv.writer(csv_file)
                writer.writerow(header)

            for b_id in beatmap_list:
                b_file = getOsuFile(b_id)
                b = obtainHitObjectArrayFromOsu(b_file)

                if b.keys != 4: continue
                print(counter, ' | ', b.name)
            
                b_calc = BeatmapCalculations(b)

                # Write to CSV
                if wcsv: 
                    row = [
                        b.beatmapid,
                        coll_name,
                        b.name,
                        np.average(b_calc.nomod.dns_roll),
                        np.average(b_calc.nomod.mnp_roll),
                        np.average(b_calc.nomod.stn_roll),
                        np.average(b_calc.nomod.rice_ttl_roll),
                        np.average(b_calc.nomod.inv_roll),
                        np.average(b_calc.nomod.rel_roll),
                        np.average(b_calc.nomod.hld_roll),
                        np.average(b_calc.nomod.lns_roll),
                        np.average(b_calc.nomod.ln_ttl_roll),
                        np.average(b_calc.nomod.ttl_roll),
                        np.average(b_calc.dt.ttl_roll)
                    ]

                    writer.writerow(row)
                    global_writer.writerow(row)

                    counter += 1

                # Plots
                if plots:
                    color = (random.random(),random.random(),random.random())
                    x = np.array([h.timestamp for h in b.hitobjects])

                    generate_subplot(dens,       x, b_calc.nomod.dns,      b_calc.nomod.dns_roll,      color, b.name, i, 'DNS - Density Component')
                    generate_subplot(manip,      x, b_calc.nomod.mnp,      b_calc.nomod.mnp_roll,      color, b.name, i, 'MNP - Manipulability Component')
                    generate_subplot(strain,     x, b_calc.nomod.stn,      b_calc.nomod.stn_roll,      color, b.name, i, 'STR - Strain Component')
                    generate_subplot(inverse,    x, b_calc.nomod.inv,      b_calc.nomod.inv_roll,      color, b.name, i, 'LN-INV - LN Inverse Component')
                    generate_subplot(release,    x, b_calc.nomod.rel,      b_calc.nomod.rel_roll,      color, b.name, i, 'LN-REL - LN Release Component')
                    generate_subplot(lnness,     x, b_calc.nomod.lns,      b_calc.nomod.lns_roll,      color, b.name, i, 'LN-LNS - LN LNness Component')
                    generate_subplot(hold,       x, b_calc.nomod.hld,      b_calc.nomod.hld_roll,      color, b.name, i, 'LN-HLD - LN Hold Strain Difficulty')
                    generate_subplot(ln_total,   x, b_calc.nomod.ln_ttl,   b_calc.nomod.ln_ttl_roll,   color, b.name, i, 'LN Total - (INV+REL)^LNS * HLD')
                    generate_subplot(rice_total, x, b_calc.nomod.rice_ttl, b_calc.nomod.rice_ttl_roll, color, b.name, i, 'RICE Total - (DNS*STR)/MNP')
                    generate_subplot(total,      x, b_calc.nomod.ttl,      b_calc.nomod.ttl_roll,      color, b.name, i, 'Total - ((DNS*STR)/MNP * (INV+REL)^LNS) * HLD')

                    i -= 0.07
        if plots:
            inverse.legend()
            plt.subplots_adjust(wspace=.5)
            plt.show()

else:
    if mode == 'ranked': 
        folder = maps_folder
    else: 
        folder = './tests/'

    fig, ((dens, inverse), (manip, release), (strain, lnness), (rice_total, hold), (total,  ln_total)) = plt.subplots(nrows=5, ncols=2, sharex=True)

    for m in os.listdir(folder):
        with open(f'{folder}{m}', 'r', encoding='utf8', errors='ignore') as b_file: 
            b = obtainHitObjectArrayFromOsu(b_file)
            if b.keys != 4: continue
            
            print(counter, ' | ', b.name)
        
            b_calc = BeatmapCalculations(b)

            #Write to CSV
            if wcsv: 
                row = [
                    b.beatmapid,
                    'ranked',
                    b.name,
                    np.average(b_calc.nomod.dns_roll),
                    np.average(b_calc.nomod.mnp_roll),
                    np.average(b_calc.nomod.stn_roll),
                    np.average(b_calc.nomod.rice_ttl_roll),
                    np.average(b_calc.nomod.inv_roll),
                    np.average(b_calc.nomod.rel_roll),
                    np.average(b_calc.nomod.hld_roll),
                    np.average(b_calc.nomod.lns_roll),
                    np.average(b_calc.nomod.ln_ttl_roll),
                    np.average(b_calc.nomod.ttl_roll),
                    np.average(b_calc.dt.ttl_roll)
                ]

                global_writer.writerow(row)
                counter += 1

            # Plots
            if plots:
                color = (random.random(),random.random(),random.random())
                x = np.array([ h.timestamp for h in b.hitobjects ])

                generate_subplot(dens,       x, b_calc.nomod.dns,      b_calc.nomod.dns_roll,      color, b.name, i, 'DNS - Density Component')
                generate_subplot(manip,      x, b_calc.nomod.mnp,      b_calc.nomod.mnp_roll,      color, b.name, i, 'MNP - Manipulability Component')
                generate_subplot(strain,     x, b_calc.nomod.stn,      b_calc.nomod.stn_roll,      color, b.name, i, 'STR - Strain Component')
                generate_subplot(inverse,    x, b_calc.nomod.inv,      b_calc.nomod.inv_roll,      color, b.name, i, 'LN-INV - LN Inverse Component')
                generate_subplot(release,    x, b_calc.nomod.rel,      b_calc.nomod.rel_roll,      color, b.name, i, 'LN-REL - LN Release Component')
                generate_subplot(lnness,     x, b_calc.nomod.lns,      b_calc.nomod.lns_roll,      color, b.name, i, 'LN-LNS - LN LNness Component')
                generate_subplot(hold,       x, b_calc.nomod.hld,      b_calc.nomod.hld_roll,      color, b.name, i, 'LN-HLD - LN Hold Strain Difficulty')
                generate_subplot(ln_total,   x, b_calc.nomod.ln_ttl,   b_calc.nomod.ln_ttl_roll,   color, b.name, i, 'LN Total - (INV+REL)^LNS * HLD')
                generate_subplot(rice_total, x, b_calc.nomod.rice_ttl, b_calc.nomod.rice_ttl_roll, color, b.name, i, 'RICE Total - (DNS*STR)/MNP')
                generate_subplot(total,      x, b_calc.nomod.ttl,      b_calc.nomod.ttl_roll,      color, b.name, i, 'Total - ((DNS*STR)/MNP * (INV+REL)^LNS) * HLD')

                i -= 0.07

    if plots:
        inverse.legend()
        plt.subplots_adjust(wspace=.5)
        plt.show()


print(time() - t)