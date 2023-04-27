"""
This script runs the Suite2P pipeline on a folder of TIF files.

Usage: python suite2p_script.py [input_path] --batch [y/n] --reclassify [y/n]

Arguments:
    input_path (str): Path to the folder containing TIF files.

Output:
    The script saves the processed data in a new folder within the input_path folder.

Dependencies:
    - argparse
    - os
    - sys
    - tifffile
    - datetime
    - suite2p

Note:
    This script assumes that the TIF files are named using the following convention:
    bigTIFF_<chunk_number>.TIF

    The script uses default Suite2P options, but these can be modified by editing the code in the section marked "set your options for running".
"""

import argparse
import os
import sys
from tifffile import *
from datetime import datetime
from suite2p import default_ops, run_s2p

# Create an argument parser
parser = argparse.ArgumentParser()

# Add a positional argument
parser.add_argument('filepath', help='Filepath to experiment(s) to run Suite2P on.')

# Add an optional argument with a default value
parser.add_argument('--batch', '-b', choices=['y', 'n'], default='y', help='Default: y. Look within directory for directories with "5minTL" in the name and run Suite2P on them.')

# Add an optional argument with a choice of values
parser.add_argument('--reclassify', '-r', choices=['y', 'n'], default='n', help='Default: n. Reclassify ROIs? (y/n). If no, will skip dataset.')

# Parse the command line arguments
args = parser.parse_args()

# Print out the arguments
print('File path:', args.filepath)
print('Batch:', args.batch)
print('Reclassify:', args.reclassify)


# Define the location of the TIF files
cmd_path = args.filepath

# Define whether batch processing or not
if args.batch == 'y':
    batch = True
else:
    batch = False

# Define whether reclassifying or not
if args.reclassify == 'y':
    reclassify = True
else:
    reclassify = False

# set your options for running
ops = default_ops() # populates ops with the default options
# https://suite2p.readthedocs.io/en/latest/settings.html
#Main settings
# ops['tau'] = 0.7 #spcific to gcamp6f
ops['fs'] = 20

#Registration
# ops['batch_size'] = 1000
# ops['smooth_sigma'] = 5
# ops['smooth_sigma_time'] = 1

#1P Registration
# ops['1Preg'] = True

#Non-rigid registration
# ops['snr_thresh'] = 1.5

#ROI detection
ops['threshold_scaling'] = 0
# Values of less than 10 are recommended for 1P data where there are often large full-field changes in brightness.
# ops['high_pass'] = 5
# ops['max_overlap'] = 1.0

#Cellpose
ops['anatomical_only'] = 1
ops['diameter'] = 52
ops['flow_threshold'] = 5
ops['cellprob_threshold'] = 0.0

#Signal extraction
ops['neuropil_extract'] = False
# ops['lam_percentile'] = 0
ops['allow_overlap'] = True

#Spike deconvolution
# ops['neucoeff'] = 0
# ops['sig_baseline'] = 1

#Classification
# ops['soma_crop'] = False
ops['classifier_path'] = '/cluster/tufts/levinlab/rellis01/calcium/juanita/5minTL.2023-02-14-15-56-28/suite2p/plane0/classifier_juanita.npy'

def get_tifs(input_path):
    # List of TIF files
    tif_files = sorted([f for f in os.listdir(input_path) if f.endswith('.tif')])
    print(f'Tif files to run: {tif_files}')
    return tif_files


def run_suite2p(ops, input_path, tif_files):
    # Run Suite2P
    # provide an h5 path in 'h5py' or a tiff path in 'data_path'
    # db overwrites any ops (allows for experiment specific settings)
    db = {
    'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
    'data_path': [input_path],# a list of folders with tiffs 
                                # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)
        'tiff_list': tif_files 
    #'input_format':'TIF'
    }

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    # RUN THE EXPERIMENT!!!
    opsEnd=run_s2p(ops=ops,db=db)
    
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


# if batch==True, run the script on all directories with '5minTL' in the name
if batch:
    # iterate over directories with '5minTL' in the name
    for dir in os.listdir(cmd_path):
        if '5min' in dir:
            if '1_175_I3C_5minTL.2023-04-11-15-47-31' in dir:
                print(f'{dir} has bugs, will come back to it')
                continue

            # if reclassify==False, skip directories that have already been processed
            if reclassify==False:
                # skip directories that have already been processed
                if os.path.isfile(os.path.join(cmd_path, dir, 'bigtiffs', 'suite2p', 'plane0', 'spks.npy')):
                    print(f'{dir} Already processed')
                    continue
                else:
                    # define the path to the directory
                    input_path = os.path.join(cmd_path, dir, 'bigtiffs')
                    print(input_path)
                    tif_files = get_tifs(input_path)
                    run_suite2p(ops, input_path, tif_files)
            
            else:
                # define the path to the directory
                input_path = os.path.join(cmd_path, dir, 'bigtiffs')
                print(input_path)
                tif_files = get_tifs(input_path)
                run_suite2p(ops, input_path, tif_files)
                
# otherwise, run the script on the directory specified in the second argument
else:
    # check if data have already been processed
    if os.path.isfile(os.path.join(cmd_path, 'bigtiffs', 'suite2p', 'plane0', 'spks.npy')):
        # if reclasify==False, skip directories that have already been processed
        if reclassify==False:
            # skip directories that have already been processed
            print(f'{dir} Already processed')
            pass
        # otherwise, run the script on the directory specified in the second argument
        else:
            input_path = os.path.join(cmd_path, 'bigtiffs')
            print(input_path)
            tif_files = get_tifs(input_path)
            run_suite2p(ops, input_path, tif_files)
    else:
        input_path = os.path.join(cmd_path, 'bigtiffs')
        print(input_path)
        tif_files = get_tifs(input_path)
        run_suite2p(ops, input_path, tif_files)


'''
This is code written for analying individual TIF images. I highly recommend not using this and 
using bigTIFFs instead because it is much faster.
'''
# # Sort image filenames by number following 'p' in filename
# framenums = []
# for tif_file in tif_files:
#     p_idx = tif_file.find('p')
#     underscore_idx = tif_file[p_idx:].find('_')
#     framenum = tif_file[p_idx+1:p_idx+underscore_idx]
#     framenums.append(int(framenum))

# # order filenames in a list
# tif_files = [tif_file for _, tif_file in sorted(zip(framenums, tif_files))]
### End of code for individual TIF images

