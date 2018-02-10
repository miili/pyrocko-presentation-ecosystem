import numpy as num
import matplotlib

matplotlib.use("Agg")
from pyrocko.gf import LocalEngine, DCSource, Target, HalfSinusoidSTF
import matplotlib.pyplot as plt
import matplotlib.animation as manimation



# stf = HalfSinusoidSTF(0.1)
dip = 15.
rake = 5.
strikes = num.linspace(-60., 20, 100)
engine = LocalEngine(store_superdirs=['.'])
store_id = 'qplayground_total_4_mr_full'
east_shifts = num.linspace(0., 10000., 25)
targets = [Target(store_id=store_id, east_shift=east_shift, north_shift=east_shift) for east_shift in east_shifts]
nshift = 10000.
depth = 10000.
offset = 0.2
ylim = len(targets)*offset

fig  = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlim(1.4, 5)
ax.set_ylim(-1., ylim)

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Seismodelic', artist='Matplotlib',
                                comment='Movie support!')
writer = FFMpegWriter(fps=10, metadata=metadata)

lines = []
for t in targets:
    l, = ax.plot([], [], color='black', linewidth=0.75)
    lines.append(l)

ax.set_xticks([])
ax.set_yticks([])
plt.subplots_adjust(left=0, right=1., bottom=0., top=1.)
with writer.saving(fig, "seismodelic.mp4", 200):
    for strike in strikes:
        sources = [DCSource(
            depth=depth, north_shift=nshift, strike=strike, dip=dip, rake=rake)]
        response = engine.process(sources=sources, targets=targets)

        trs = response.pyrocko_traces()
        scale = num.max([tr.ydata for tr in trs])
        for itr, tr in enumerate(trs):
            tr.lowpass(4, 12.)
            tr.highpass(4, .1)
            lines[itr].set_data(tr.get_xdata(), tr.get_ydata()/scale +itr * offset)

        writer.grab_frame()
