import sys
sys.path.append("../")
from helper_funs import *
import re

sys(f'hspice osfet_model_run.sp -o')

def generate_figname():
    ii = 0
    pwdpath = os.path.dirname(os.path.realpath(__file__))
    while os.path.isfile(os.path.join(pwdpath, f'temp{ii}.png')):
        ii = ii+1
    return f'temp{ii}.png'

main_directory_path = os.path.dirname(os.path.realpath(__file__))
num_datasets, df_list = read_lis_modified(fname=os.path.join(main_directory_path, "osfet_model_run.lis"), sweep_variable='vgate')
print(df_list[0].columns)
id_list = [df['current_vs'] for df in df_list]
vg_list = [df['voltage_g'] for df in df_list]

c = ['r']
s = ['solid']
a = [0.5, 1]
logy_lin_plot_dual(x1=vg_list, y1=id_list, x2=vg_list, y2=id_list, c1=c, c2=c, s1=s, s2=s, a1=a, a2=a, lw=4.0, figname=generate_figname())
