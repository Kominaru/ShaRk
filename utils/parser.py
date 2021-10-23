import numpy as np
import matplotlib.pyplot as plt

class HitObject:
    def __init__(self, column, timestamp, lnend=0) -> None:
        self.column = column
        self.timestamp = timestamp
        self.isln = lnend > 0
        self.lnend = lnend


def obtainHitObjectArrayFromOsu(file):
    hitobjects = []
    l = file.readline()
    while "[HitObjects]" not in l:
        l = file.readline()

    while True:
        l = file.readline()
        if not l:
            break
        lineinfo = l.split(',')
        column = (int(lineinfo[0])-64)//128
        timestamp = int(lineinfo[2])
        lnend = int(lineinfo[5].split(":")[0])
        hitobjects.append(HitObject(column, timestamp, lnend))

    return hitobjects

def generate_subplot(subplot,x,raw,roll,color,map,i,title):
    
    subplot.plot(x,raw,c=color,alpha=0.05)
    subplot.plot(x,roll,label=map,c=color,linewidth=3)
    subplot.text(0.8,i,s=f"{map[:12]+'...'}: {np.average(roll):0.2f}",horizontalalignment='left',
                verticalalignment='center',
                transform = subplot.transAxes)
    subplot.title.set_text(title)