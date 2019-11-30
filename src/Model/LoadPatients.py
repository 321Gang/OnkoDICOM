"""
./src/Model/LoadPatients.py
This file contains basic functions for loading original dicom files.
The output returned consists of two dictionaries, one contains the
file paths of read files and the other the data obtained from each file
after reading the data.
"""

import glob
import re

import pydicom


def natural_sort(file_list):
    """
    Sort filenames.

    :param file_list:   List of dcm file names.
    
    :return:            Sorted list of all file names.
    """
    # Logger info
    print('Natural Sorting...')
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(file_list, key=alphanum_key)


def get_datasets(path):
    """
    Read patient directory and return dictionary of read data and file names.

    :param path: str, path of patient directory
    
    :return read_data_dict: dict, data read from files in patient directory
    
    :return file_names_dict: dict, the paths to all files read
    """

    # Data contains data read from files
    # Key is int for ct images and str (rtdose, rtss, rtplan) for RT files
    read_data_dict = {}

    # Data contains file paths
    # Key is int for ct images and str (rtdose, rtss, rtplan) for RT files
    file_names_dict = {}

    # Sort files based on name
    dcm_files = natural_sort(glob.glob(path + '/*'))
    i = 0  # For key values for ct images

    # For each file in path
    for file in dcm_files:
        try:
            read_file = pydicom.dcmread(file, force=True)
        except:
            pass
        else:
            if 'SOPClassUID' in read_file:
                if read_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.2':
                    read_data_dict[i] = read_file
                    file_names_dict[i] = file
                    i += 1
                elif read_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.481.3':
                    read_data_dict['rtss'] = read_file
                    file_names_dict['rtss'] = file
                elif read_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.481.2':
                    read_data_dict['rtdose'] = read_file
                    file_names_dict['rtdose'] = file
                elif read_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.481.5':
                    read_data_dict['rtplan'] = read_file
                    file_names_dict['rtplan'] = file
            
    return read_data_dict, file_names_dict