import numpy as np
import os
from numpy.lib.function_base import average
import random
import csv
from utils.osu_api import extractBeatmapIds, getOsuFile

from utils.parser import *

from time import time
from config import Config

import pyqtgraph
from pyqtgraph import QtGui, QtCore


class Main():

    def __init__(self):
        # CSV header row
        self.header = ['Beatmap ID', 'Collection Name', 'Chart Name', 'Density', 'Manipulability', 'Strain',
                       'Rhythm', 'RICE TOTAL', 'Inverse', 'Release', 'Hold', 'LNNess', 'LN TOTAL', 'GLOBAL', 'DT GLOBAL']
        self.maps_folder = './mapas/'
        self.collections_folder = './collections/'

        self.csv_writer = None

        t = time()

        os.makedirs('csvs', exist_ok=True)
        os.makedirs('cached_maps', exist_ok=True)

        if Config.wcsv:
            csv_file = open('./CSVS/ALL.csv', 'w', encoding='UTF8', newline='')
            self.csv_writer = csv.writer(csv_file)
            self.csv_writer.writerow(self.header)

        if Config.plots:
            self.__build_gui()

        if Config.mode == Config.MODE_COLLECTIONS:
            self.run_collections_mode()

        if Config.mode == Config.MODE_RANKED:
            self.run_ranked_mode()

        print(time() - t)

        if Config.plots:
            self.__select_data_idx(0)
            self.app.exec_()

    def __build_gui(self):
        self.app = pyqtgraph.mkQApp('Mania plots')

        self.map_list = QtGui.QListWidget()
        self.map_list.currentRowChanged.connect(self.__select_data_idx)
        self.selected_layout = None
        self.plot_layouts = []

        self.main_widget = QtGui.QWidget()
        self.main_layout = QtGui.QHBoxLayout(self.main_widget)
        self.main_layout.addWidget(self.map_list)

        self.main_widget.resize(1000, 600)
        self.main_widget.setWindowTitle('Mania plots')

        pyqtgraph.setConfigOptions(antialias=True)
        self.main_widget.show()

    def run_collections_mode(self):
        counter = 1
        folder = './tests/'

        # Identify all collections in collections folder
        for coll in os.listdir(self.collections_folder):
            coll_name = coll.split('.')[0]
            with open(f'{self.collections_folder}{coll}', 'r', encoding='utf8', errors='ignore') as f:
                # Find all beatmap IDs in the file
                beatmap_list = extractBeatmapIds(f.read())

                # Prepare CSV collection
                if Config.wcsv:
                    csv_file = open(
                        f'./csvs/{coll_name}.csv', 'w', encoding='UTF8', newline='')
                    writer = csv.writer(csv_file)
                    writer.writerow(self.header)

                for b_id in beatmap_list:
                    b_file = getOsuFile(b_id)
                    b = obtainHitObjectArrayFromOsu(b_file)

                    if b.keys != 4:
                        continue

                    print(counter, ' | ', b.name)

                    b_calc = BeatmapCalculations(b)

                    # Write to CSV
                    if Config.wcsv:
                        row = [
                            b.beatmapid,
                            coll_name,
                            b.name,
                            np.average(b_calc.nomod.dns_roll),
                            np.average(b_calc.nomod.mnp_roll),
                            np.average(b_calc.nomod.stn_roll),
                            np.average(b_calc.nomod.rhy_roll),
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
                        self.global_writer.writerow(row)

                        counter += 1

                    # Plots
                    if Config.plots:
                        color = (random.randint(0, 255), random.randint(
                            0, 255), random.randint(0, 255))
                        x = np.array([h.timestamp for h in b.hitobjects])

                        plot_layout = pyqtgraph.GraphicsLayoutWidget()

                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.dns,      b_calc.nomod.dns_roll,      color, b.name, 'DNS - Density Component')
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.mnp,      b_calc.nomod.mnp_roll,      color, b.name, 'MNP - Manipulability Component')
                        plot_layout.nextRow()
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.stn,      b_calc.nomod.stn_roll,      color, b.name, 'STR - Strain Component')
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.rhy,      b_calc.nomod.rhy_roll, color, b.name, 'RHY - Rhythm Complexity Component')

                        plot_layout.nextRow()
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.inv,      b_calc.nomod.inv_roll,      color, b.name, 'LN-INV - LN Inverse Component')
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.rel,      b_calc.nomod.rel_roll,      color, b.name, 'LN-REL - LN Release Component')

                        plot_layout.nextRow()
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.lns,      b_calc.nomod.lns_roll,      color, b.name, 'LN-LNS - LN LNness Component')
                        self.__generate_subplot(plot_layout, x, b_calc.nomod.hld,      b_calc.nomod.hld_roll,
                                                color, b.name, 'LN-HLD - LN Hold Strain Difficulty')
                        plot_layout.nextRow()
                        self.__generate_subplot(
                            plot_layout, x, b_calc.nomod.ln_ttl,   b_calc.nomod.ln_ttl_roll,   color, b.name, 'LN Total - (INV+REL)^LNS * HLD')
                        self.__generate_subplot(plot_layout, x, b_calc.nomod.rice_ttl,
                                                b_calc.nomod.rice_ttl_roll, color, b.name, 'RICE Total - (DNS*STR)/MNP')
                        plot_layout.nextRow()
                        self.__generate_subplot(plot_layout, x, b_calc.nomod.ttl,      b_calc.nomod.ttl_roll,
                                                color, b.name, 'Total - ((DNS*STR)/MNP * (INV+REL)^LNS) * HLD')

                        self.plot_layouts.append(plot_layout)
                        self.map_list.addItem(QtGui.QListWidgetItem(b.name))
                        self.main_layout.addWidget(plot_layout)
                        plot_layout.hide()

    def run_ranked_mode(self):
        counter = 1
        folder = self.maps_folder

        for m in os.listdir(folder):
            with open(f'{folder}{m}', 'r', encoding='utf8', errors='ignore') as b_file:
                b = obtainHitObjectArrayFromOsu(b_file)
                if b.keys != 4:
                    continue

                print(counter, ' | ', b.name)

                b_calc = BeatmapCalculations(b)

                # Write to CSV
                if Config.wcsv:
                    row = [
                        b.beatmapid,
                        'ranked/loved',
                        b.name,
                        np.average(b_calc.nomod.dns_roll),
                        np.average(b_calc.nomod.mnp_roll),
                        np.average(b_calc.nomod.stn_roll),
                        np.average(b_calc.nomod.rhy_roll),
                        np.average(b_calc.nomod.rice_ttl_roll),
                        np.average(b_calc.nomod.inv_roll),
                        np.average(b_calc.nomod.rel_roll),
                        np.average(b_calc.nomod.hld_roll),
                        np.average(b_calc.nomod.lns_roll),
                        np.average(b_calc.nomod.ln_ttl_roll),
                        np.average(b_calc.nomod.ttl_roll),
                        np.average(b_calc.dt.ttl_roll)
                    ]

                    self.csv_writer.writerow(row)
                    counter += 1

                # Plots
                if Config.plots:
                    color = (random.randint(0, 255), random.randint(
                        0, 255), random.randint(0, 255))
                    x = np.array([h.timestamp for h in b.hitobjects])

                    plot_layout = pyqtgraph.GraphicsLayoutWidget()

                    self.__generate_subplot(plot_layout, x, b_calc.nomod.dns,
                                            b_calc.nomod.dns_roll,      color, b.name, 'DNS - Density Component')
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.mnp,
                                            b_calc.nomod.mnp_roll,      color, b.name, 'MNP - Manipulability Component')
                    plot_layout.nextRow()
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.stn,
                                            b_calc.nomod.stn_roll,      color, b.name, 'STR - Strain Component')
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.rhy,      b_calc.nomod.rhy_roll,
                                            color, b.name, 'RHY - Rhythm Complexity Component')

                    plot_layout.nextRow()
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.inv,
                                            b_calc.nomod.inv_roll,      color, b.name, 'LN-INV - LN Inverse Component')
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.rel,
                                            b_calc.nomod.rel_roll,      color, b.name, 'LN-REL - LN Release Component')

                    plot_layout.nextRow()
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.lns,
                                            b_calc.nomod.lns_roll,      color, b.name, 'LN-LNS - LN LNness Component')
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.hld,      b_calc.nomod.hld_roll,
                                            color, b.name, 'LN-HLD - LN Hold Strain Difficulty')

                    self.__generate_subplot(plot_layout, x, b_calc.nomod.ln_ttl,
                                            b_calc.nomod.ln_ttl_roll,   color, b.name, 'LN Total - (INV+REL)^LNS * HLD')
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.rice_ttl,
                                            b_calc.nomod.rice_ttl_roll, color, b.name, 'RICE Total - (DNS*STR)/MNP')
                    plot_layout.nextRow()
                    self.__generate_subplot(plot_layout, x, b_calc.nomod.ttl,      b_calc.nomod.ttl_roll,
                                            color, b.name, 'Total - ((DNS*STR)/MNP * (INV+REL)^LNS) * HLD')

                    self.plot_layouts.append(plot_layout)
                    self.map_list.addItem(QtGui.QListWidgetItem(b.name))
                    self.main_layout.addWidget(plot_layout)
                    plot_layout.hide()

    def __generate_subplot(self, plot_layout, x, raw, roll, color, map, title):
        # return plot_layout.addPlot(x=x, y=raw, title=title, color=color, name=map)
        return plot_layout.addPlot(x=x, y=roll, title=title, pen=color)

    def __select_data_idx(self, idx):
        selected_layout = self.plot_layouts[idx]
        if self.selected_layout == selected_layout:
            return

        if type(self.selected_layout) != type(None):
            self.selected_layout.hide()

        self.selected_layout = selected_layout
        self.selected_layout.show()


if __name__ == '__main__':
    Main()
