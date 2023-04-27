import numpy as np
import sys
import os

'''
The purpose of this script is to take a subset of the cells and ROIs from the Suite2P output and 
save them as a new npy file.
'''

# Define the path to the Suite2P output
root = sys.argv[1]
print(root)

# create an empty list to store the subdirectories
subdirectories = []

# traverse directories and subdirectories using os.walk()
for dirpath, dirnames, filenames in os.walk(root):
    # append the subdirectories in the current directory to the list if they contain '5min'
    for dirname in dirnames:
        if '5min' in dirname:
            subdirectories.append(os.path.join(dirpath, dirname))

# iterate over the subdirectories and save a subsetted spks array for the cell ROIs
for dir in subdirectories:
    print(dir)
    # check if 'spks.npy' exists in the directory
    if os.path.isfile(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'spks.npy')):
        # check if 'cell_spks.npy' exists in the directory
        if os.path.isfile(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'cell_spks.npy')):
            print('cell_spks.npy already exists')
            continue
        else:
            spks = np.load(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'spks.npy'))
            iscell = np.load(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'iscell.npy'))
            cell_spks = spks[iscell[:,0]==1,:]
            np.save(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'cell_spks.npy'), cell_spks)
            print('cell_spks.npy saved')
    else:
        print('spks.npy does not exist')
        continue
        