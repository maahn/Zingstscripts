import os

# Set paths where raw data is located
IPATH = 'data/'


def main():

    # Prepare KT19 data
    clean_merge_kt19_data()

    # Prepare Pyrgeometer data
    clean_merge_pyr_data()

    # Prepare IR thermometer data
    clean_merge_ir_data()


def clean_merge_pyr_data():
    # Set paths and open merged file
    ipath_pyr_data, f_all = set_paths('pyr')

    # Loop through raw data files
    for file in sorted(os.listdir(ipath_pyr_data)):
        if not file.startswith('.'):
            # Open file from raw data
            f = open(os.path.join(ipath_pyr_data, file), 'r')
            # Loop through lines to check for valid format
            for nl, line in enumerate(f):
                line_split = line.split()
                # Write to merged file if format is valid
                if len(line_split) == 20:
                    f_all.write(line)


def clean_merge_ir_data():
    # Set paths and open merged file
    ipath_ir_data, f_all = set_paths('ir')

    # Loop through raw data files
    file_list = [file for file in sorted(os.listdir(ipath_ir_data)) if file.endswith('xls')]
    for nf, file in enumerate(file_list):
        if not file.startswith('.') and file.endswith('xls'):
            # Open file from raw data
            f = open(os.path.join(ipath_ir_data, file), 'r')
            # Loop through lines to check for valid format
            for nl, line in enumerate(f):
                # We only need the header of the file once, so only write it once, else jump to next line
                if nf == 0 and nl == 0:
                    f_all.write(line)
                else:
                    # Write to merged file if format is valid
                    line_split = line.split()
                    if len(line_split) == 6:
                        f_all.write(line)


def clean_merge_kt19_data():
    # Set paths and open merged file
    ipath_kt19_data, f_all = set_paths('kt19')

    # Loop through raw data files
    for file in sorted(os.listdir(ipath_kt19_data)):
        if not file.startswith('.'):
            # Open file from raw data
            f = open(os.path.join(ipath_kt19_data, file), 'rb')
            # Loop through lines to check for valid format
            for line_byte in f:
                # Check for faulty bytes
                try:
                    line = line_byte.decode('utf-8')
                except UnicodeDecodeError:
                    continue
                line_split = line.split()
                # Check line for valid format
                if len(line_split) == 8 and line.count('\r') == 1:
                    # Make sure all entries are digits
                    try:
                        _ = [float(entry) for entry in line_split]
                    except ValueError:
                        continue
                    # Write to merged file if format is valid
                    f_all.write(line)


def set_paths(instr):
    # Set path for raw data
    ipath_raw_data = os.path.join(IPATH, 'raw', instr)

    # Set file path for merged file
    file_all = os.path.join(IPATH, 'processed', f'{instr}_data_all.dat')

    # Clean up previous run
    if os.path.isfile(file_all):
        os.remove(file_all)

    # Open merged file for writing
    f_all = open(file_all, 'w')

    return ipath_raw_data, f_all


if __name__ == "__main__":
    main()
