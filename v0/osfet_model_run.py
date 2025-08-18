from helper_funs import *
from TLM_OSFETs import *
import re

def generate_figname():
    ii = 0
    pwdpath = os.path.dirname(os.path.realpath(__file__))
    while os.path.isfile(os.path.join(pwdpath, f'temp{ii}.png')):
        ii = ii+1
    return f'temp{ii}.png'

""" split double sweep into fwd and bkd sweeps """
def get_sweeps(X):
    N1 = len(X)
    X_ = {}
    X_['f'] = X[:int(N1/2)]
    X_['b'] = X[int(N1/2):]
    return X_

# Define the directory to start the search (current working directory)
start_directory = os.path.join(os.path.dirname(os.getcwd()), "benchmarking_data")

# List to store relative paths to all CSV files
csv_files = []

# Walk through the directory and subdirectories
for root, dirs, files in os.walk(os.path.join(start_directory)):
    for file in files:
        if file.endswith('.csv'):
            # Get the absolute path of the file
            absolute_path = os.path.abspath(os.path.join(root, file))
            if 'IGNORE' in absolute_path:
                continue
            # Add to the dictionary
            csv_files.append(absolute_path)

def get_params(file):
    RDL_match = re.search(r'R\[(\d+)\]_D\[(\d+)\]_L\[(\d+)\]', file)
    
    extracted_params = {
        'R': int(RDL_match.group(1)) if RDL_match else None,
        'D': int(RDL_match.group(2)) if RDL_match else None,
        'L': int(RDL_match.group(3)) if RDL_match else None
    }
    return extracted_params

exp_dict = {'R': 4, 'D': 6, 'L': 60}
for cf in csv_files:
    if not 'IdVg_Vd_par' in cf:
        continue
    cf_dict = get_params(cf)
    print(cf, cf_dict)
    if exp_dict == cf_dict:
        break

exp_data_fname = cf
print(exp_data_fname)
pd_data_set, N1 = agilent_csv_cleaner(fname=exp_data_fname)
if len(pd_data_set) > 2:
    raise Exception('More than 2 datasets detected')

Vg_all = [get_sweeps(d[' Vg'].to_numpy()) for d in pd_data_set[:2]]
Id_all = [get_sweeps(d[' absIs'].to_numpy()) for d in pd_data_set[:2]]
xvg = [vg['f'][::2] for vg in Vg_all]
yid = [id['f'][::2] for id in Id_all]
# xvg += [vg['b'] for vg in Vg_all]
# yid += [id['b'] for id in Id_all]

Vglin = xvg[-2]
Idlin = yid[-2]
Vdlin = 50e-3
T = 300
PHIT = kB*300
BETA, nSSlin, VTONlin, VTOFFlin, TRlin = calculate_VTON_VTOFF(Vglin, Idlin*1e6/2, Vdlin, PHIT, Id_SS_limits=[1e-5, 1e-1])
print(BETA, nSSlin, VTONlin, VTOFFlin, TRlin)

# c = ['r', 'b']
# s = ['solid']*2
# a = [1]*2
# mask = [True, True]

# logy_lin_plot_dual(x1=xvg, y1=[id*1e6/2 for id in yid], x2=xvg, y2=[id*1e6/2 for id in yid], c1=c, c2=c, s1=s, s2=s, a1=a, a2=a, mask=mask, lw=4.0, xlabel="$\mathbf{Vg [V]}$", ylabel="$\mathbf{Id [uA/um]}$", figname=generate_figname())

sys(f'hspice osfet_model_run.sp -o')

main_directory_path = os.path.dirname(os.path.realpath(__file__))
num_datasets, df_list = read_lis_modified(fname=os.path.join(main_directory_path, "osfet_model_run.lis"), sweep_variable='vgate')
print(df_list[0].columns)
yid += [df['current_vs'].to_numpy() for df in df_list]
xvg += [df['voltage_g'].to_numpy() for df in df_list]

# c = ['r']
# s = ['solid']
# a = [0.5, 1]
# logy_lin_plot_dual(x1=vg_list, y1=id_list, x2=vg_list, y2=id_list, c1=c, c2=c, s1=s, s2=s, a1=a, a2=a, lw=4.0, figname=generate_figname())

c = ['r', 'b']
s = ['None']*2+['solid']*2
m = ['o']*2+[None]*2
a = [1]*2
mask = [True, True]
logy_lin_plot_dual(x1=xvg, y1=[id*1e6/2 for id in yid], x2=xvg, y2=[id*1e6/2 for id in yid], c1=c, c2=c, s1=s, s2=s, a1=a, a2=a, m1=m, m2=m, mask=mask, lw=4.0, xlabel="$\mathbf{Vg [V]}$", ylabel="$\mathbf{Id [uA/um]}$", figname=generate_figname(), ylim=[1e-6, 1e3])