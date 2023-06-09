import numpy as np
import os
import seaborn as sns
import sys
from time import gmtime, strftime
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # Define the path to the Suite2P output
    root = sys.argv[1]
    print(root)

    # whether to overwrite existing files
    overwrite = sys.argv[2] # 'True' or 'False' for overwriting existing files

    # raw fluorescence (F.npy) or deconvolved (spks.npy) data; 'raw' or 'deconvolved'
    data_type = sys.argv[3]

    # create an empty list to store the subdirectories
    subdirectories = []

    # traverse directories and subdirectories using os.walk()
    for dirpath, dirnames, filenames in os.walk(root):
        # append the subdirectories in the current directory to the list if they contain '5min'
        for dirname in dirnames:
            if '5min' in dirname:
                subdirectories.append(os.path.join(dirpath, dirname))

    # iterate over the subdirectories and save a subsetted spks array for the cell ROIs
    for sdir in subdirectories:
        print(sdir)
        # check if 'F.npy' exists in the directory
        if data_type == 'raw':
            filecheck = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F.npy')
            if os.path.isfile(filecheck):
                # initialize filename
                filename = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F_traveling_wave_plot.png')
            else: print(f'{filecheck} does not exist'); continue
        elif data_type == 'deconvolved':
            filecheck = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'spks.npy')
            if os.path.isfile(filecheck):    
                # initialize filename
                filename = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'spks_traveling_wave_plot.png')
            else: print(f'{filecheck} does not exist'); continue
        else:
            print("Incorrect data_type parameter. Must use 'raw' or 'deconvolved'")

        # check if the file already exists and overwrite is set to False
        if os.path.isfile(filename) and not overwrite:
            print(f'{filename} already exists')

        # otherwise, run the plotting code
        else:
            print(f'Making traveling wave plot')
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

            # Load data and remove first 1000 frames (lots of photobleaching)
            data = np.load(filecheck)
            iscell = np.load(os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'iscell.npy'))   
            data = data[iscell[:, 0] == 1]
            data = data[:, 1000:6000]

            # max values for each cell (row)
            max_indices = np.argmax(data, axis=1)

            # sort the max values by time
            sort_indices = np.argsort(max_indices)

            # sort the data
            sort_data = data[sort_indices]

            # sort the data in 1d to calculate max for color bar
            sort_1d = np.sort(data.ravel())

            tw_plot = sns.heatmap(sort_data, cmap='binary', vmin=0, vmax=sort_1d[int(0.9995*(len(sort_1d)))])

            # Save the figure to a file
            slash_idx = sdir.find('/')
            plt.title(f"{sdir[slash_idx+1:]}")
            plt.savefig(f"{filename}", dpi=300)
            plt.clf()
            print(f'{sdir} saved')
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))  

