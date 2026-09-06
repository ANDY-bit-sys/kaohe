"""Experiment 2: separate open/short/load OP runs, original vs Thevenin circuit."""
from common import *

VS, R1, R2 = 12., 1000., 2000.
VTH, RTH = VS*R2/(R1+R2), R1*R2/(R1+R2)

def network(load=None, equivalent=False, short=False):
    c = Circuit('Thevenin equivalent' if equivalent else 'Original two-terminal network')
    c.V('s','supply',0,VTH if equivalent else VS)
    c.R(1,'supply','a',RTH if equivalent else R1)
    if not equivalent:
        c.R(2,'a',0,R2)
    if short:
        # A 0 V voltage source is an ideal ammeter, with current positive from a to b.
        c.V('short','a',0,0)
    elif load is not None:
        c.R('load','a',0,load)
    return c

def schematic():
    d = drawing()
    d += elm.SourceV().at((0,0)).up().length(3).label('Vs = 12 V')
    d += elm.Resistor().right().length(3.5).label('R1 = 1 kΩ')
    d += elm.Dot()
    d += elm.Resistor().down().length(3).label('R2 = 2 kΩ',loc='bottom')
    d += elm.Line().to((0,0))
    d += elm.Line().at((3.5,3)).right().length(2)
    d += elm.Dot(open=True).label('a (+)',loc='right')
    d += elm.Line().at((3.5,0)).right().length(2)
    d += elm.Dot(open=True).label('b (0 V)',loc='right')
    d += elm.Ground().at((3.5,0))
    save_drawing(d,'thevenin_original')
    d = drawing()
    d += elm.SourceV().at((0,0)).up().length(3).label('Vth = 8 V')
    d += elm.Resistor().right().length(4).label('Rth = 666.667 Ω')
    d += elm.Dot().label('a',loc='right')
    d += elm.Resistor().down().length(3).label('RL (100 Ω to 10 kΩ)',loc='bottom')
    d += elm.Dot().label('b',loc='right')
    d += elm.Line().to((0,0))
    d += elm.Ground().at((2,0))
    save_drawing(d,'thevenin_equivalent')

def main():
    sim = simulator(network())
    op = sim.operating_point(); save_netlist(sim,'thevenin_open')
    voc = scalar(op['a'])
    sim = simulator(network(short=True))
    op = sim.operating_point(); save_netlist(sim,'thevenin_short')
    isc = scalar(op.branches['vshort'])
    rows = [comparison('Open-circuit voltage',VTH,voc,'V'),
            comparison('Short-circuit current',VS/R1*1e3,isc*1e3,'mA'),
            comparison('Thevenin resistance',RTH,voc/isc,'ohm')]
    loads = [100.,470.,1000.,2000.,10000.]
    data, checks = [], []
    for load in loads:
        measured = []
        for equivalent in [False,True]:
            sim = simulator(network(load=load,equivalent=equivalent))
            op = sim.operating_point()
            save_netlist(sim,f'thevenin_{"equivalent" if equivalent else "original"}_{int(load)}ohm')
            measured.append(scalar(op['a']))
        theory = VTH*load/(RTH+load)
        original, eq = measured
        checks += [comparison(f'RL={load:g} original voltage',theory,original,'V',1e-5),
                   comparison(f'RL={load:g} equivalent voltage',theory,eq,'V',1e-5)]
        data.append([load,theory,original,eq,theory/load*1e3,original/load*1e3,eq/load*1e3])
    values = np.asarray(data)
    save_csv('thevenin_loads',['RL_ohm','theory_V','original_V','equivalent_V','theory_mA','original_mA','equivalent_mA'],values.T)
    fig, axes = plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for ax,theory_col,orig_col,eq_col,unit in [(axes[0],1,2,3,'Voltage (V)'),(axes[1],4,5,6,'Current (mA)')]:
        ax.semilogx(values[:,0],values[:,theory_col],color='#96a3b2',label='Theory')
        ax.semilogx(values[:,0],values[:,orig_col],'o',color=BLUE,label='Original (OP)')
        ax.semilogx(values[:,0],values[:,eq_col],'x',color=ORANGE,ms=8,label='Equivalent (OP)')
        ax.set(xlabel='Load resistance (ohm)',ylabel=unit); ax.legend()
    fig.suptitle('Thevenin validation | same terminal behavior under five loads')
    save_figure(fig,'thevenin_loads')
    schematic()
    finish('thevenin',sim,rows,load_checks=checks,load_table=data,
           load_columns=['RL_ohm','theory_V','original_V','equivalent_V','theory_mA','original_mA','equivalent_mA'])

if __name__ == '__main__':
    main()
