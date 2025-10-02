# alias python3=/home/kj2011/python/Python-3.12.7/Python-3.12.7/Python/bin/python3
from helper_funs import *
from TLM_OSFETs import *
import re
import yaml
import shutil
# from gc_array_tr_process import *

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

start_directory = os.getcwd() # Get the current working directory

""" Load parameters from .yaml file """
with open(os.path.join(start_directory, "yaml_params", "test_example.yaml"), 'r') as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

Nrows = params['Nrows']
Ncols = params['Ncols']
selected_wl_idx = params['selected_wl_idx'] # index of the selected wordline to write and read, 0 to Nrows-1
wwl_en = np.zeros(Nrows).astype(int) # array of length Nrows, 1 to enable, 0 to disable
rwl_en = np.zeros(Nrows).astype(int) # array of length Nrows, 1 to enable, 0 to disable
wwl_en[selected_wl_idx] = 1
rwl_en[selected_wl_idx] = 1
print(f"wwl_en: {wwl_en}")
print(f"rwl_en: {rwl_en}")
binary_str = np.binary_repr(params['wword'])[-Ncols:].zfill(Ncols)
wword = np.array(list(binary_str)).astype(int) # array of length Ncols, 1 to write 1, 0 to write 0
print(f"wword: {wword}")
vsn_init = np.zeros((Nrows, Ncols)).astype(int) # 2D array of size Nrows x Ncols, initial voltages of each storage node
vsn_init[Nrows-1, Ncols-1] = 0 # set the last cell initial vsn

header_path = os.path.join(start_directory, "array_tb_generator", "header.txt")
read_params_path = os.path.join(start_directory, "array_tb_generator", "read_params.txt")
subckts_path = os.path.join(start_directory, "array_tb_generator", "subckts.txt")

# Replace placeholders with values from params
header_text = replace_params(open(header_path, 'r').read(), params)
# print(header_text)
read_params_text = replace_params(open(read_params_path, 'r').read(), params)
# print(read_params_text)
subckts_text = replace_params(open(subckts_path, 'r').read(), params)
# print(subckts_text)

final_text = header_text + '\n' + read_params_text + '\n' + subckts_text + '\n'

for ii in range(Nrows):
    for jj in range(Ncols):
        final_text += f".DCVOLT sn_{ii}_{jj} '{vsn_init[ii][jj]}*vdd + {1-vsn_init[ii][jj]}*vss'\n"

# for jj in range(Ncols):
#     final_text += f".DCVOLT rbl_{jj} 'vdd'\n"

for ii in range(Nrows):
    for jj in range(Ncols):
        final_text += f'xgc_{ii}_{jj} wwl_{ii}_{jj} wbl_{ii}_{jj} rwl_{ii}_{jj} rbl_{ii}_{jj} sn_{ii}_{jj} wos_ros_gc\n'
        if ii == 0 and jj == 0:
            final_text += f'xrc_wwl_{ii}_{jj} wwl_{ii} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl\n'
            final_text += f'xrc_wbl_{ii}_{jj} wbl_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl\n'
            final_text += f'xrc_rwl_{ii}_{jj} rwl_{ii} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl\n'
            final_text += f'xrc_rbl_{ii}_{jj} rbl_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl\n'
        elif ii == 0 and jj != 0:
            final_text += f'xrc_wwl_{ii}_{jj} wwl_{ii}_{jj-1} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl\n'
            final_text += f'xrc_wbl_{ii}_{jj} wbl_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl\n'
            final_text += f'xrc_rwl_{ii}_{jj} rwl_{ii}_{jj-1} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl\n'
            final_text += f'xrc_rbl_{ii}_{jj} rbl_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl\n'
        elif jj == 0 and ii != 0:
            final_text += f'xrc_wwl_{ii}_{jj} wwl_{ii} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl\n'
            final_text += f'xrc_wbl_{ii}_{jj} wbl_{ii-1}_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl\n'
            final_text += f'xrc_rwl_{ii}_{jj} rwl_{ii} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl\n'
            final_text += f'xrc_rbl_{ii}_{jj} rbl_{ii-1}_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl\n'
        else:
            final_text += f'xrc_wwl_{ii}_{jj} wwl_{ii}_{jj-1} wwl_{ii}_{jj} rc_unit R0=Rwwl C0=Cwwl\n'
            final_text += f'xrc_wbl_{ii}_{jj} wbl_{ii-1}_{jj} wbl_{ii}_{jj} rc_unit R0=Rwbl C0=Cwbl\n'
            final_text += f'xrc_rwl_{ii}_{jj} rwl_{ii}_{jj-1} rwl_{ii}_{jj} rc_unit R0=Rrwl C0=Crwl\n'
            final_text += f'xrc_rbl_{ii}_{jj} rbl_{ii-1}_{jj} rbl_{ii}_{jj} rc_unit R0=Rrbl C0=Crbl\n'

wwl_pwl_list = params['wwl_pwl_list'].split(' ')
rwl_pwl_list = params['rwl_pwl_list'].split(' ')
wbl_pwl_list = params['wbl_pwl_list'].split(' ')
for ii in range(Nrows):
    final_text += f"vww_{ii} wwl_{ii} 0 PWL({' '.join([wd if kk%2 == 0 else f"'{int(wd)*wwl_en[ii]}*vpp+{1-int(wd)*wwl_en[ii]}*vnn'" for kk, wd in enumerate(wwl_pwl_list)])})\n"
    final_text += f"vrw_{ii} rwl_{ii} 0 PWL({' '.join([rd if kk%2 == 0 else f"'{int(rd)*rwl_en[ii]}*vdd+{1-int(rd)*rwl_en[ii]}*vss'" for kk, rd in enumerate(rwl_pwl_list)])})\n"

for jj in range(Ncols):
    final_text += f"vwb_{jj} wbl_{jj} 0 PWL({' '.join([bd if kk%2 == 0 else f"'{int(bd)*wword[jj]}*vdd+{1-int(bd)*wword[jj]}*vss'" for kk, bd in enumerate(wbl_pwl_list)])})\n"
    final_text += f"vrb_{jj} rbl_{jj} 0 DC='vss'\n"

footer_path = os.path.join(start_directory, "array_tb_generator", "footer.txt")
footer_text = replace_params(open(footer_path, 'r').read(), params)
# print(footer_text)
final_text += footer_text

# print(final_text)

final_run_file = 'gc_array'
sim_out_file = 'gc_array'
with open(f"{final_run_file}.sp", 'w') as fp:
    fp.write(final_text)
fp.close()

""" run hspice in a separate directory """
sp_run_dir = "array_sp_run_tmp"
if not os.path.exists(os.path.join(os.getcwd(), sp_run_dir)):
    os.makedirs(os.path.join(os.getcwd(), sp_run_dir))

shutil.copy(f"{final_run_file}.sp", os.path.join(os.getcwd(), sp_run_dir, f"{final_run_file}.sp"))
shutil.copy(params["va_model_path"], os.path.join(os.getcwd(), sp_run_dir, os.path.basename(params["va_model_path"])))
os.chdir(os.path.join(os.getcwd(), sp_run_dir))
print("Current working directory changed to:", os.getcwd())
sys(f'hspice {final_run_file}.sp -o {sim_out_file}')
os.chdir(os.path.dirname(os.getcwd()))
print("Current working directory restored to:", os.getcwd())
# shutil.copy(os.path.join(os.getcwd(), sp_run_dir, f"{sim_out_file}.lis"), os.path.join(os.getcwd(), f"{sim_out_file}.lis"))
# shutil.copy(os.path.join(os.getcwd(), sp_run_dir, f"{sim_out_file}.tr0"), os.path.join(os.getcwd(), f"{sim_out_file}.tr0"))
