"""Experiment 3: NMOS common-source OP, small-signal AC, and transient gain."""
from common import *

VDD, RG1, RG2, RD = 5., 60e3, 40e3, 2e3
K, VTO, LAM = .8e-3, 1., .02
CB, AMPLITUDE, FREQUENCY = 10e-6, .01, 1000.
# Convention: Id = K*(Vgs-Vto)^2*(1+lambda*Vds).
# Ngspice LEVEL=1 uses KP/2*(W/L); set KP=2*K and W=L explicitly.
VGS = VDD*RG2/(RG1+RG2)
VOV = VGS-VTO
ID = K*VOV**2*(1+LAM*VDD)/(1+K*VOV**2*LAM*RD)
VDS = VDD-ID*RD
GM = 2*K*VOV*(1+LAM*VDS)
GDS = K*VOV**2*LAM
RO = 1/GDS
AV = -GM/(1/RD+GDS)

def make_circuit():
    c = Circuit('NMOS common-source amplifier')
    c.V('dd','vdd',0,VDD)
    c.V('in','vin',0,f'DC 0 AC 1 SIN(0 {AMPLITUDE} {FREQUENCY})')
    c.R('g1','vdd','gate',RG1)
    c.R('g2','gate',0,RG2)
    c.C('b1','vin','gate',CB)
    c.R('d','vdd','drain',RD)
    c.model('NM','NMOS',level=1,kp=2*K,vto=VTO,lambda_=LAM,gamma=0)
    c.M(1,'drain','gate',0,0,model='NM',w=10e-6,l=10e-6)
    return c

def schematic(dc=False):
    d = drawing()
    # Reverse the MOS symbol so the gate faces the bias network at the left.
    m = d.add(elm.NFet(bulk=True).reverse().at((6,3)))
    d += elm.Label().at((8.4,2.1)).label('M1 (NMOS)\nB tied to S')
    gx,gy = m.gate
    sx,sy = m.source
    dx,dy = m.drain
    d += elm.Line().at(m.source).to((sx,0))
    d += elm.Ground()
    bx,by = m.bulk
    d += elm.Line().at(m.bulk).right().length(.6)
    d += elm.Line().to((bx+.6,0))
    d += elm.Line().to((sx,0))
    d += elm.Resistor().at(m.drain).up().to((dx,5.6)).label('Rd = 2 kΩ',loc='bottom')
    d += elm.Line().left().to((2.5,5.6))
    d += elm.Dot().at((dx,5.6)).label('VDD = 5 V',loc='top')
    d += elm.Resistor().at((2.5,5.6)).down().to((2.5,gy)).label('Rg1 = 60 kΩ',loc='top')
    d += elm.Dot()
    d += elm.Line().to(m.gate)
    d += elm.Resistor().at((2.5,gy)).down().to((2.5,0)).label('Rg2 = 40 kΩ',loc='bottom')
    d += elm.Line().to((sx,0))
    d += elm.Line().at(m.drain).right().length(1.6)
    d += elm.Dot(open=True).label('Vo = Vd',loc='right')
    if dc:
        d += elm.Line().at((2.5,gy)).left().length(.7)
        d += elm.Dot(open=True).label('Cb1 open (DC)',loc='left')
    else:
        d += elm.Capacitor().at((-.5,gy)).right().to((2.5,gy)).label('Cb1 = 10 µF')
        d += elm.SourceSin().at((-.5,0)).up().to((-.5,gy)).label('Vi\n10 mV peak\n1 kHz')
        d += elm.Line().at((-.5,0)).to((2.5,0))
    save_drawing(d,'mos_dc_path' if dc else 'mos_schematic')

def small_signal():
    d = drawing()
    d += elm.SourceSin().at((0,0)).up().length(3).label('vi = vgs')
    d += elm.Line().right().length(2.4)
    d += elm.Dot().label('g',loc='top')
    d += elm.Resistor().down().length(3).label('Rg1 || Rg2\n24 kΩ',loc='bottom')
    d += elm.Line().to((0,0))
    d += elm.Ground().at((1,0))
    d += elm.SourceControlledI().at((7,3)).down().length(3).label('gm·vgs',loc='top')
    d += elm.Line().right().length(7)
    d += elm.Ground().at((10.5,0))
    d += elm.Resistor().at((10.5,3)).down().length(3).label('ro\n62.5 kΩ',loc='bottom')
    d += elm.Resistor().at((14,3)).down().length(3).label('Rd\n2 kΩ',loc='bottom')
    d += elm.Line().at((7,3)).to((14,3))
    d += elm.Dot().at((10.5,3)).label('d / vo',loc='top')
    d += elm.Label().at((7,-1)).label('Midband: Cb1 short; VDD is AC ground; source and bulk grounded')
    save_drawing(d,'mos_small_signal')

def main():
    sim = simulator(make_circuit())
    # Device parameters must be explicitly saved to expose gm and gds in OP output.
    # PySpice 1.5 mutates its "all" option when serializing. Explicit vectors survive repeated runs.
    sim.save(['v(gate)','v(drain)','v(vin)','v(vdd)','i(vdd)','i(vin)',
              '@m1[gm]','@m1[gds]','@m1[id]'])
    op = sim.operating_point(); save_netlist(sim,'mos_op')
    vg,vd = scalar(op['gate']),scalar(op['drain'])
    id_sim,gm_sim,gds_sim = (scalar(op.internal_parameters[f'@m1[{p}]']) for p in ['id','gm','gds'])
    if not (vg>VTO and vd>=vg-VTO):
        raise AssertionError('MOS is not in saturation at the OP')
    rows = [comparison('VGS',VGS,vg,'V',1e-5),comparison('ID',ID*1e3,id_sim*1e3,'mA',1e-5),
            comparison('VDS',VDS,vd,'V',1e-5),comparison('gm',GM*1e3,gm_sim*1e3,'mS',1e-5),
            comparison('ro',RO,1/gds_sim,'ohm',1e-5)]
    # AC/transient need only voltages. Separate simulators avoid converting internal OP
    # conductances into complex AC waveforms in PySpice 1.5.
    sim = simulator(make_circuit())
    ac = sim.ac(variation='lin',number_of_points=1,start_frequency=FREQUENCY,stop_frequency=FREQUENCY)
    save_netlist(sim,'mos_ac','.ac lin 1 1000 1000')
    ac_gain = complex(np.asarray(ac['drain'])[0]/np.asarray(ac['vin'])[0])
    rg = RG1*RG2/(RG1+RG2)
    coupling = (2j*np.pi*FREQUENCY*rg*CB)/(1+2j*np.pi*FREQUENCY*rg*CB)
    expected_ac = AV*coupling
    rows.append(comparison('Gain at 1kHz (AC magnitude)',abs(expected_ac),abs(ac_gain),'V/V',1e-5))
    transient = sim.transient(step_time=2e-6,end_time=.03,max_time=2e-6)
    save_netlist(sim,'mos_transient','.tran 2u 30m 0 2u')
    t,vi,vg_wave,vo = map(np.asarray,[transient.time,transient['vin'],transient['gate'],transient['drain']])
    selected = t>=.02
    input_phasor,_ = sinusoid_fit(t[selected],vi[selected],FREQUENCY)
    output_phasor,offset = sinusoid_fit(t[selected],vo[selected],FREQUENCY)
    measured_gain = output_phasor/input_phasor
    rows.append(comparison('Gain (transient signed real)',AV,measured_gain.real,'V/V',.005))
    phase = float(np.angle(measured_gain,deg=True))
    if abs(abs(phase)-180)>.5:
        raise AssertionError('Output is not inverted')
    if not np.all(vo[selected] >= vg_wave[selected]-VTO):
        raise AssertionError('Transient leaves saturation')
    save_csv('mos_transient',['time_s','vin_V','vgs_V','vout_V'],[t,vi,vg_wave,vo])
    shown = t>=.025
    fig,axes = plt.subplots(3,1,figsize=(10,9),sharex=True,layout='constrained')
    axes[0].plot(t[shown]*1e3,vi[shown]*1e3,color=BLUE,label='Vin (10 mV peak)')
    axes[0].set(ylabel='Input (mV)',title='NMOS common-source | measured transient response'); axes[0].legend()
    axes[1].plot(t[shown]*1e3,vo[shown],color=ORANGE,label='Drain output including DC bias')
    axes[1].axhline(VDS,color='gray',ls=':',label=f'DC theory: {VDS:.5f} V')
    axes[1].set(ylabel='Output (V)'); axes[1].legend()
    axes[2].plot(t[shown]*1e3,vi[shown]*1e3,color=BLUE,label='Input AC')
    axes[2].plot(t[shown]*1e3,(vo[shown]-offset)*1e3,color=ORANGE,label='Output AC (mean removed)')
    axes[2].set(xlabel='Time (ms)',ylabel='AC voltage (mV)',title=f'Gain = {measured_gain.real:.5f} V/V | phase = {phase:.3f} deg'); axes[2].legend()
    save_figure(fig,'mos_transient')
    schematic(); schematic(dc=True); small_signal()
    finish('mos',sim,rows,convention='Id = K*(Vgs-Vto)^2*(1+lambda*Vds); KP=2*K; W=L=10um',
           parameters={'K_A_per_V2':K,'KP_A_per_V2':2*K,'lambda_per_V':LAM,'Cb1_F':CB,'input_peak_V':AMPLITUDE,'frequency_Hz':FREQUENCY},
           saturation={'VDS_V':vd,'VOV_V':vg-VTO,'DC_passed':True,'last_10ms_passed':True},
           theory_gain=AV,ac_gain_real=ac_gain.real,ac_gain_imag=ac_gain.imag,
           transient_gain_real=measured_gain.real,transient_phase_deg=phase,
           input_peak_measured_V=abs(input_phasor),output_peak_measured_V=abs(output_phasor),fit_window_s=[.02,.03])

if __name__ == '__main__':
    main()
