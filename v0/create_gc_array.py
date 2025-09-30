from os import system as sys
import fileinput as fi
import os
import re
import yaml

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

Rwire = params['Rwire']
Cwire = params['Cwire']
Nrows = params['Nrows']
Ncols = params['Ncols']
wwl_en = params['wwl_en']
rwl_en = params['rwl_en']

wword = params['wword']
vsn_init = params['vsn_init']