#!/usr/bin/env python3
import sys
import numpy as num

from pyrocko.gf import LocalEngine, DCSource, Target
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

km = 1e3

ntraces = 25
nframes = 100
trace_offset = 0.1

store_id = 'qplayground_total_4_mr_full'
store_id = 'crust2_gc'
engine = LocalEngine(store_superdirs=['.'])

ls = num.linspace
dips = ls(60, 60, nframes)
rakes = ls(0., 10., nframes)
strikes = ls(-180., 180, nframes)
depths = ls(4*km, 4*km, nframes)
east_shifts = ls(100., 200*km, ntraces)
nshift = 5*km

targets = [
    Target(
        store_id=store_id,
        east_shift=east_shift,
        north_shift=east_shift)
    for east_shift in east_shifts]

ylim = ntraces*trace_offset

fig = plt.figure()
ax = fig.add_subplot(111, facecolor='black')

ax.set_xlim(-20, 75)
ax.set_ylim(-2., ylim)

lines = []
for t in targets:
    l, = ax.plot([], [],
                 color='white',
                 alpha=.8,
                 linewidth=0.75,
                 animated=True)
    lines.append(l)

ax.set_xticks([])
ax.set_yticks([])
plt.subplots_adjust(left=0, right=1., bottom=0., top=1.)

source = DCSource()


def update_plot(iframe, *args):
    source.depth = depths[iframe]
    source.north_shift = nshift
    source.strike = strikes[iframe]
    source.dip = dips[iframe]
    source.rake = rakes[iframe]

    response = engine.process(
        sources=[source],
        targets=targets)

    trs = response.pyrocko_traces()
    scale = num.max([tr.ydata.max() for tr in trs])

    for itr, tr in enumerate(trs):
        tr.extend(tmin=ax.get_xlim()[0], tmax=ax.get_xlim()[1],
                  fillmethod="repeat")
        # tr.lowpass(4, .4)
        # tr.highpass(4, .1)
        lines[itr].set_data(
            tr.get_xdata(),
            tr.get_ydata()/scale + itr * trace_offset)
    ax.relim()

    return lines


if __name__ == '__main__':
    ani = manimation.FuncAnimation(
        fig, update_plot, interval=50, frames=nframes, blit=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        ani.save('traces.gif', dpi=80, writer='imagemagick')
    else:
        plt.show()
