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
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .22, 'axes.titleweight': 'bold'})
BLUE, ORANGE = '#2375b8', '#d66625'

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
    d.config(unit=2.4, fontsize=12, color='#17334a', lw=1.8)
    return d

def save_drawing(d, name):
    d.save(str(OUT / (name + '.svg')))
    d.save(str(OUT / (name + '.png')), dpi=170)
    plt.close('all')

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
