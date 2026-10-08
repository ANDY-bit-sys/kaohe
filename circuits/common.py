"""Shared plotting/output helpers; circuit definitions live in the three experiment files."""
import json
import os
from pathlib import Path
import tempfile
import platform
import importlib.metadata

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(ROOT.parent / 'tmp' / 'matplotlib'))
# Ngspice 34 on Windows can fail to locate its init file through a Chinese path.
# An ASCII temporary path lets it load this minimal init file; these circuits need no XSPICE plugins.
_spice_init = tempfile.TemporaryDirectory(prefix='kaohe-spice-')
Path(_spice_init.name, 'spinit').write_text('set num_threads=1\n', encoding='ascii')
os.environ['SPICE_SCRIPTS'] = _spice_init.name

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_S
import schemdraw
import schemdraw.elements as elm

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 170, 'font.size': 11,
                     'font.family': 'sans-serif',
                     'font.sans-serif': ['Microsoft YaHei', 'DejaVu Sans'],
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .22, 'axes.titleweight': 'bold'})
BLUE, ORANGE = '#2375b8', '#d66625'
SCHEMATIC_BLUE, SCHEMATIC_INK = '#2475D8', '#193650'
SCHEMATIC_FONT = 'Microsoft YaHei'

def simulator(circuit):
    sim = circuit.simulator(temperature=27, nominal_temperature=27)
    # PySpice 1.5 omits the Ngspice "admittance" unit mapping used by gm and gds.
    sim.ngspice._type_to_unit.setdefault(sim.ngspice.simulation_type.admittance, u_S)
    sim.options(reltol=1e-7, abstol=1e-12, vntol=1e-9)
    return sim

def scalar(wave):
    return float(np.asarray(wave).reshape(-1)[0])

def save_figure(fig, name):
    fig.savefig(OUT / (name + '.png'), bbox_inches='tight', facecolor='white')
    plt.close(fig)

def drawing():
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.4, inches_per_unit=.65, fontsize=13,
             font=SCHEMATIC_FONT, color=SCHEMATIC_BLUE, lw=1.8,
             bgcolor='white', margin=.32)
    return d

def save_drawing(d, name, title, note=''):
    # Keep textbook symbols blue and conductors/connection points dark.
    for element in d.elements:
        if isinstance(element, (elm.Line, elm.Dot, elm.Ground)):
            element.color(SCHEMATIC_INK)
    figure = d.draw(show=False)
    figure.ax.set_title(title, loc='left', fontname=SCHEMATIC_FONT,
                        fontsize=16, fontweight='normal', color=SCHEMATIC_INK, pad=24)
    if note:
        figure.ax.text(0, -.09, note, transform=figure.ax.transAxes,
                       ha='left', va='top', fontname=SCHEMATIC_FONT,
                       fontsize=12, color=SCHEMATIC_BLUE, linespacing=1.6)
    canvas = figure.getfig()
    for extension in ['svg', 'png']:
        path = OUT / (name + '.' + extension)
        canvas.savefig(path, bbox_inches='tight',
                       facecolor='white', transparent=False, pad_inches=.25, dpi=180)
        if extension == 'svg':
            # Matplotlib emits spaces at the ends of SVG path-data lines.
            content = path.read_text(encoding='utf-8')
            path.write_text('\n'.join(line.rstrip() for line in content.splitlines()) + '\n',
                            encoding='utf-8')
    plt.close(canvas)

def save_csv(name, columns, data):
    np.savetxt(OUT / (name + '.csv'), np.column_stack(data), delimiter=',',
               header=','.join(columns), comments='', fmt='%.12g')

def save_netlist(sim, name, analysis='.op'):
    # PySpice removes the analysis directive after a run; restore it for standalone reuse.
    deck = str(sim).replace('.end', analysis + '\n.end')
    (OUT / (name + '.cir')).write_text(deck, encoding='utf-8')

def comparison(name, theoretical, measured, unit, tolerance=.01):
    error = abs(measured-theoretical) / max(abs(theoretical), 1e-20)
    if not np.isfinite(measured) or error > tolerance:
        raise AssertionError(f'{name}: theory={theoretical}, simulation={measured}, error={error:.3%}')
    return {'quantity': name, 'theory': theoretical, 'simulation': measured,
            'unit': unit, 'relative_error_percent': 100*error, 'passed': True}

def finish(name, sim, rows, **details):
    result = {'experiment': name, 'python': platform.python_version(),
              'PySpice': importlib.metadata.version('PySpice'),
              'ngspice': sim.ngspice.ngspice_version,
              'comparisons': rows, **details}
    (OUT / (name + '_results.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))

def sinusoid_fit(t, values, frequency):
    # A signed complex phasor avoids treating an inverted output as a positive gain.
    w = 2*np.pi*frequency*t
    matrix = np.column_stack([np.sin(w), np.cos(w), np.ones_like(w)])
    sin, cos, offset = np.linalg.lstsq(matrix, values, rcond=None)[0]
    return complex(sin, cos), float(offset)
