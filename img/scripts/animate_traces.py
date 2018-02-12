import sys
import numpy as num

from pyrocko.gf import LocalEngine, DCSource, Target
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

km = 1e3

nframes = 100
trace_offset = 0.1

store_id = 'qplayground_total_4_mr_full'
engine = LocalEngine(store_superdirs=['.'])

ls = num.linspace
dips = ls(0, 360, nframes)
rakes = ls(5., 5., nframes)
strikes = ls(-180., 180, nframes)
depths = ls(10*km, 10*km, nframes)
east_shifts = ls(0., 10*km, 25)
nshift = 10*km

targets = [
    Target(store_id=store_id, east_shift=east_shift, north_shift=east_shift)
    for east_shift in east_shifts]

ylim = len(targets)*trace_offset

fig = plt.figure()
ax = fig.add_subplot(111, facecolor='black')

ax.set_xlim(1.4, 5)
ax.set_ylim(-1., ylim)

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
    scale = num.max([tr.ydata for tr in trs])

    for itr, tr in enumerate(trs):
        tr.lowpass(4, 12.)
        tr.highpass(4, .1)
        lines[itr].set_data(
            tr.get_xdata(),
            tr.get_ydata()/scale + itr * trace_offset)

    return lines


if __name__ == '__main__':
    ani = manimation.FuncAnimation(
        fig, update_plot, interval=50, frames=nframes, blit=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        ani.save('traces.gif', dpi=80, writer='imagemagick')
    else:
        fig.show()
