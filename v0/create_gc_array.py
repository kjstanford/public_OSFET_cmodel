from os import system as sys
import fileinput as fi

Rwire = 1e2
Cwire = 1e-15
params = dict(
            mu_eff=20e-4, W=60e-9, Lch=60e-9, Cgch=0.0124, Cpar=0.0124*60e-9, longVT=0.3, alpha1=0.52, alpha2=0.05, meff=0.3, rsd_mode=0, Rs0=200e-6, Rd0=200e-6, n0=1.4433, nd=0.0, delta=0.06, rollVT=0.0, type=1, \
            vsup = 0.9, step = 1e-12, sim_time = 30e-9, \
            vhold = 0, vboost = 1.2, wwl_del = 2e-9, wwl_rise = 100e-12, wwl_fall = 100e-12,  wwl_pw = 1e-9, wwl_tp = 100e-9, \
            vread = 0.9, rwl_del = 20e-9, rwl_rise = 100e-12, rwl_fall = 100e-12,  rwl_pw = 1e-9, rwl_tp = 100e-9, \
            vnone = 0, vwbit = 0.9, wbl_del = 2e-9, wbl_rise = 100e-12, wbl_fall = 100e-12,  wbl_pw = 1.2e-9, wbl_tp = 100e-9, \
            Rwwl = Rwire, Cwwl = Cwire, Rwbl = Rwire, Cwbl = Cwire, Rrwl = Rwire, Crwl = Cwire, Rrbl = Rwire, Crbl = Cwire \
            )

Nrows = 1024 # num of word lines
Ncols = 32 # word length
wwl_en = [0]*Nrows
rwl_en = [0]*Nrows
wwl_en[-1] = 1 # worst case row
rwl_en[-1] = 1 # worst case row
# wword = [0, 1, 0, 1, 1, 0, 0, 1] # test word
wword = [1]*Ncols # worst case column
vsn_init = [[0 for _ in range(Ncols)] for _ in range(Nrows)]

is_lines = list(fi.input(files = f'create_gc_array_starter.txt'))
starter = []

for line in is_lines:
    line_list = line.split()
    if len(line_list) == 4:
        if line_list[0] == ".PARAM" and line_list[3] == 'xxx':
            line_list[3] = str(params[line_list[1]])
    starter.append(' '.join(line_list))

for ii in range(Nrows):
    for jj in range(Ncols):
        starter.append(f".DCVOLT sn_{ii}_{jj} {vsn_init[ii][jj]}")

gc_netlist = [' ']
for ii in range(Nrows):
    for jj in range(Ncols):
        gc_netlist.append(f'xgc_{ii}_{jj} wwl_{ii}_{jj} wbl_{ii}_{jj} rwl_{ii}_{jj} rbl_{ii}_{jj} sn_{ii}_{jj} wos_ros_gc')
        if ii == 0 and jj == 0:
            gc_netlist.append(f'xrc_wwl_{ii}_{jj} wwl_{ii} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl')
            gc_netlist.append(f'xrc_wbl_{ii}_{jj} wbl_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl')
            gc_netlist.append(f'xrc_rwl_{ii}_{jj} rwl_{ii} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl')
            gc_netlist.append(f'xrc_rbl_{ii}_{jj} rbl_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl')
        elif ii == 0 and jj != 0:
            gc_netlist.append(f'xrc_wwl_{ii}_{jj} wwl_{ii}_{jj-1} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl')
            gc_netlist.append(f'xrc_wbl_{ii}_{jj} wbl_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl')
            gc_netlist.append(f'xrc_rwl_{ii}_{jj} rwl_{ii}_{jj-1} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl')
            gc_netlist.append(f'xrc_rbl_{ii}_{jj} rbl_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl')
        elif jj == 0 and ii != 0:
            gc_netlist.append(f'xrc_wwl_{ii}_{jj} wwl_{ii} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl')
            gc_netlist.append(f'xrc_wbl_{ii}_{jj} wbl_{ii-1}_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl')
            gc_netlist.append(f'xrc_rwl_{ii}_{jj} rwl_{ii} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl')
            gc_netlist.append(f'xrc_rbl_{ii}_{jj} rbl_{ii-1}_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl')
        else:
            gc_netlist.append(f'xrc_wwl_{ii}_{jj} wwl_{ii}_{jj-1} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl')
            gc_netlist.append(f'xrc_wbl_{ii}_{jj} wbl_{ii-1}_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl')
            gc_netlist.append(f'xrc_rwl_{ii}_{jj} rwl_{ii}_{jj-1} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl')
            gc_netlist.append(f'xrc_rbl_{ii}_{jj} rbl_{ii-1}_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl')

signal_netlist = [' ']
for ii in range(Nrows):
    signal_netlist.append(f"vww_{ii} wwl_{ii} 0 PULSE 'vhold' '{wwl_en[ii]}*vboost' 'wwl_del' 'wwl_rise' 'wwl_fall' 'wwl_pw' 'wwl_tp'")
    signal_netlist.append(f"vrw_{ii} rwl_{ii} 0 PULSE '0' '{rwl_en[ii]}*vread' 'rwl_del' 'rwl_rise' 'rwl_fall' 'rwl_pw' 'rwl_tp'")

for jj in range(Ncols):
    signal_netlist.append(f"vwb_{jj} wbl_{jj} 0 PULSE 'vnone' '{wword[jj]}*vwbit' 'wbl_del' 'wbl_rise' 'wbl_fall' 'wbl_pw' 'wbl_tp'")
    signal_netlist.append(f"vrb_{jj} rbl_{jj} 0 DC=0")

ie_lines = list(fi.input(files = f'create_gc_array_ender.txt'))
ender = []

for line in ie_lines:
    line_list = line.split()
    if len(line_list) == 4:
        if line_list[0] == ".PARAM" and line_list[3] == 'xxx':
            line_list[3] = str(params[line_list[1]])
    ender.append(' '.join(line_list))

with open(f'gc_array.sp', 'w') as fp:
    fp.write('\n'.join(starter+gc_netlist+signal_netlist+ender))
fp.close()

sys(f'hspice gc_array.sp -o')