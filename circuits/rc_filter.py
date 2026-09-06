"""Experiment 1: RC low-pass, actual PySpice transient + AC simulations."""
from common import *

R, C = 10_000., 100e-9
TAU, FC = R*C, 1/(2*np.pi*R*C)

def make_circuit():
    circuit = Circuit('RC low-pass R=10k C=100n')
    # 0-to-1 V square wave, 50 Hz. AC 1 gives H(jw) directly in the AC analysis.
    circuit.V('in', 'vin', 0, 'DC 0 AC 1 PULSE(0 1 1m 1u 1u 10m 20m)')
    circuit.R(1, 'vin', 'vout', R)
    circuit.C(1, 'vout', 0, C)
    return circuit

def schematic():
    d = drawing()
    d += elm.SourceSquare().at((0,0)).up().length(3).label('Vin: 0-1 V\n50 Hz')
    d += elm.Resistor().right().length(4).label('R = 10 kΩ')
    d += elm.Dot().label('Vout', loc='top')
    d += elm.Capacitor().down().length(3).label('C = 100 nF', loc='bottom')
    d += elm.Line().to((0,0))
    d += elm.Ground().at((2,0))
    save_drawing(d, 'rc_schematic')

def main():
    sim = simulator(make_circuit())
    transient = sim.transient(step_time=10e-6, end_time=.05, max_time=10e-6)
    save_netlist(sim, 'rc_transient', '.tran 10u 50m 0 10u')
    t, vi, vo = map(np.asarray, [transient.time, transient['vin'], transient['vout']])
    # Measure the first 63.212% crossing; use the midpoint of the finite 1 us input rise.
    select = (t >= .001) & (t <= .006)
    crossing = np.interp(1-np.exp(-1), vo[select], t[select])
    tau_measured = crossing - .0010005
    ac = sim.ac(variation='dec', number_of_points=200, start_frequency=1, stop_frequency=1e5)
    save_netlist(sim, 'rc_ac', '.ac dec 200 1 100k')
    f, h = np.asarray(ac.frequency), np.asarray(ac['vout']) / np.asarray(ac['vin'])
    db = 20*np.log10(abs(h))
    cutoff_db = -10*np.log10(2)
    fc_measured = 10**np.interp(cutoff_db, db[::-1], np.log10(f[::-1]))
    theory = 1/(1+2j*np.pi*f*TAU)
    rows = [comparison('Time constant', TAU*1e3, tau_measured*1e3, 'ms', .002),
            comparison('Cutoff frequency', FC, fc_measured, 'Hz', .002)]
    save_csv('rc_transient', ['time_s','vin_V','vout_V'], [t,vi,vo])
    save_csv('rc_ac', ['frequency_Hz','gain_dB','phase_deg'], [f,db,np.angle(h,deg=True)])
    fig, axes = plt.subplots(2,1, figsize=(10,7), layout='constrained')
    axes[0].plot(t*1e3,vi,label='Input square wave',color=BLUE)
    axes[0].plot(t*1e3,vo,label='Output (Ngspice)',color=ORANGE)
    axes[0].set(title='RC low-pass | square-wave response', xlabel='Time (ms)',ylabel='Voltage (V)')
    axes[0].legend()
    tt = t[select]-.0010005
    axes[1].plot(tt*1e3,vo[select],color=ORANGE,label='Ngspice')
    axes[1].plot(tt*1e3,1-np.exp(-np.maximum(tt,0)/TAU),'--',color=BLUE,label='Ideal-step theory')
    axes[1].axvline(tau_measured*1e3, color='#587955',ls=':',label=f'Measured tau = {tau_measured*1e3:.4f} ms')
    axes[1].set(xlabel='Time from input rise midpoint (ms)',ylabel='Output (V)',title='First charging edge | 63.212% crossing')
    axes[1].legend()
    save_figure(fig,'rc_transient')
    fig, axes = plt.subplots(2,1,figsize=(10,7),sharex=True,layout='constrained')
    axes[0].semilogx(f,db,color=ORANGE,label='Ngspice')
    axes[0].semilogx(f,20*np.log10(abs(theory)),'--',color=BLUE,label='Theory')
    axes[0].axhline(cutoff_db,ls=':',color='gray')
    axes[0].axvline(fc_measured,ls=':',color='gray',label=f'fc = {fc_measured:.3f} Hz')
    axes[0].set(title='RC low-pass | Bode plot',ylabel='Gain (dB)'); axes[0].legend()
    axes[1].semilogx(f,np.angle(h,deg=True),color=ORANGE,label='Ngspice')
    axes[1].semilogx(f,np.angle(theory,deg=True),'--',color=BLUE,label='Theory')
    axes[1].set(xlabel='Frequency (Hz)',ylabel='Phase (degrees)'); axes[1].legend()
    save_figure(fig,'rc_bode')
    schematic()
    finish('rc',sim,rows,parameters={'R_ohm':R,'C_F':C,'pulse_Hz':50,'rise_time_s':1e-6},
           measurement='tau: 63.212% crossing; fc: interpolated -3.0103 dB crossing')

if __name__ == '__main__':
    main()
