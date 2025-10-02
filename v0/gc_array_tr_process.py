import re
import numpy as np
from typing import List, Dict, Any

def read_hspice_tr_sw_ac(filename: str) -> List[Dict[str, Any]]:
    """
    Read HSPICE .tr, .sw, or .ac simulation output files.
    Returns a list of dictionaries with 'var_name' and 'val' (data array).
    """
    # Determine file extension
    file_extension = filename[-3:].lower()

    # Read file content, skip first 3 header lines
    with open(filename, 'r') as f:
        lines = f.readlines()[3:]  # Skip first 3 lines

    content_str = [line.strip() for line in lines if line.strip()]

    # Find start of data marked by '$&%#'
    try:
        data_start_idx = content_str.index('$&%#') + 1
    except ValueError:
        raise ValueError("Data marker '$&%#' not found in file.")

    # Extract header lines (before data) to determine number of variables
    header_lines = content_str[:data_start_idx - 1]
    num_var = 0
    for line in header_lines:
        try:
            if np.isnan(float(line.split()[0])):
                break
            num_var += 1
        except (ValueError, IndexError):
            continue

    # Extract variable names
    var_name_raw = []
    i = num_var
    while i < len(header_lines):
        line = header_lines[i]
        if '(' in line and ')' not in line:
            # Multi-line name: combine with next line
            if i + 1 < len(header_lines):
                combined = line + header_lines[i + 1]
                var_name_raw.append(combined)
                i += 2
            else:
                var_name_raw.append(line)
                i += 1
        else:
            var_name_raw.append(line)
            i += 1

    # Handle .ac files: split real/imaginary parts
    simulation_result = []
    if file_extension in ['.tr', '.sw']:
        for name in var_name_raw:
            simulation_result.append({'var_name': name, 'val': np.array([])})
    elif file_extension == '.ac':
        var_names = []
        for i, name in enumerate(var_name_raw):
            # Assume every 7th variable (starting at 1) has real/imag parts
            if (i + 1) % 7 == 1:
                var_names.append(name + '_real')
                var_names.append(name + '_imag')
            else:
                var_names.append(name)
        for name in var_names:
            simulation_result.append({'var_name': name, 'val': np.array([])})
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    # Parse data section
    data_section = ' '.join(content_str[data_start_idx:])
    # Match numbers in scientific notation (e.g., 1.234E+03, -5.67E-02)
    data_matches = re.findall(r'[-+]?\d*\.\d+E[+-]?\d+|[-+]?\d+E[+-]?\d+', data_section)
    data_numeric = np.array([float(x) for x in data_matches])

    # Assign data to each signal in round-robin fashion
    n_signals = len(simulation_result)
    n_points = len(data_numeric) // n_signals

    if n_points * n_signals != len(data_numeric):
        raise ValueError("Data length is not divisible by number of signals.")

    for i in range(n_signals):
        simulation_result[i]['val'] = data_numeric[i::n_signals]

    return simulation_result
