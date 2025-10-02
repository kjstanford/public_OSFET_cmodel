# alias python3=/home/kj2011/python/Python-3.12.7/Python-3.12.7/Python/bin/python3
from helper_funs import *
from TLM_OSFETs import *
import re
import yaml
import shutil

""" important functions defined below """
def replace_params(text, params):
    pattern = re.compile(r'@(\w+)@')

    def is_number(s):
        # Helper to check if s can be interpreted as a number
        try:
            float(s)
            return True
        except ValueError:
            return False

    def replacer(match):
        key = match.group(1)
        value = params.get(key, match.group(0))

        # Only add quotes if it's a string and NOT a number
        if isinstance(value, str) and not is_number(value):
            if not (value.startswith('"') and value.endswith('"')) and not (value.startswith("'") and value.endswith("'")):
                value = f'"{value}"'
        return str(value)

    return pattern.sub(replacer, text)

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

# exp_data_fname = os.path.join(start_directory, "chihsin_ito_v3", "IdVg_Vd_par [R[4]_D[6]_L[60] ; ].csv")
exp_data_fname = os.path.join(start_directory, "chihsin_ito_W_L_Lov_60nm", "ITO_Wch_60_25_02.csv")
print(exp_data_fname)
pd_data_set, N1 = agilent_csv_cleaner(fname=exp_data_fname)
if len(pd_data_set) > 2:
    raise Exception('More than 2 datasets detected')

# Vg_all = [get_sweeps(d[' Vg'].to_numpy()) for d in pd_data_set[:2]]
# Id_all = [get_sweeps(d[' absIs'].to_numpy()) for d in pd_data_set[:2]]
Vg_all = [get_sweeps(d[' VG'].to_numpy()) for d in pd_data_set[:2]]
Id_all = [get_sweeps(d[' IDS'].to_numpy()) for d in pd_data_set[:2]]
xvg = [vg['f'][::2] for vg in Vg_all]
yid = [id['f'][::2] for id in Id_all]

# Vglin = xvg[-2]
# Idlin = yid[-2]
# Vdlin = 50e-3
Vglin = xvg[-1]
Idlin = yid[-1]
Vdlin = 100e-3
T = 300
PHIT = kB*300
BETA, nSSlin, VTONlin, VTOFFlin, TRlin = calculate_VTON_VTOFF(Vglin, Idlin*1e6/2, Vdlin, PHIT, Id_SS_limits=[1e-5, 1e-1])
print(BETA, PHIT*nSSlin*log(10)*1e3, VTONlin, VTOFFlin, TRlin)

""" Load parameters from .yaml file """
# with open(os.path.join(start_directory, "chihsin_ito_v3", "yaml_params", "IdVg_Vd_par [R[4]_D[6]_L[60] ; ].yaml"), 'r') as f:
with open(os.path.join(start_directory, "chihsin_ito_W_L_Lov_60nm", "ITO_Wch_60_25_02.yaml"), 'r') as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

sp_template_path = os.path.join(os.getcwd(), params["sp_template_path"])
final_runfile = "osfet_model_run"
sp_final_runfile_path = os.path.join(os.getcwd(), f"{final_runfile}.sp")

""" create the hspice netlist + testbench """
# Read the template file
with open(sp_template_path, 'r') as file:
    text = file.read()

# Replace placeholders with values from params
new_text = replace_params(text, params)

# create the final sp runfile
with open(sp_final_runfile_path, 'w') as file:
    file.write(new_text)

""" run hspice in a separate directory """
sp_run_dir = "sp_run_tmp"
if not os.path.exists(os.path.join(os.getcwd(), sp_run_dir)):
    os.makedirs(os.path.join(os.getcwd(), sp_run_dir))

shutil.copy(sp_final_runfile_path, os.path.join(os.getcwd(), sp_run_dir, f"{final_runfile}.sp"))
shutil.copy(params["va_model_path"], os.path.join(os.getcwd(), sp_run_dir, os.path.basename(params["va_model_path"])))
os.chdir(os.path.join(os.getcwd(), sp_run_dir))
print("Current working directory changed to:", os.getcwd())
sys(f'hspice osfet_model_run.sp -o')
os.chdir(os.path.dirname(os.getcwd()))
print("Current working directory restored to:", os.getcwd())
shutil.copy(os.path.join(os.getcwd(), sp_run_dir, f"{final_runfile}.lis"), os.path.join(os.getcwd(), f"{final_runfile}.lis"))
shutil.copy(os.path.join(os.getcwd(), sp_run_dir, f"{final_runfile}.sw0"), os.path.join(os.getcwd(), f"{final_runfile}.sw0"))

""" parse the .lis file and plot """
main_directory_path = os.path.dirname(os.path.realpath(__file__))
num_datasets, df_list = read_lis_modified(fname=os.path.join(main_directory_path, "osfet_model_run.lis"), sweep_variable='vgate')
print(df_list[0].columns)
yid += [df['current_vs'].to_numpy() for df in df_list]
xvg += [df['voltage_g'].to_numpy() for df in df_list]

c = ['r', 'b', 'b', 'r']
s = ['None']*2+['solid']*2
m = ['o']*2+[None]*2
a = [1]*2
mask = [True, True, True, True]
logy_lin_plot_dual(x1=xvg, y1=[id*1e6/2 for id in yid], x2=xvg, y2=[id*1e6/2 for id in yid], c1=c, c2=c, s1=s, s2=s, a1=a, a2=a, m1=m, m2=m, mask=mask, lw=4.0, xlabel="$\mathbf{Vg [V]}$", ylabel="$\mathbf{Id [uA/um]}$", figname=generate_figname(), ylim=[1e-6, 1.5], xlim=[0, 1.3])