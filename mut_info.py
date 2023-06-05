import numpy as np
import os
from sklearn.feature_selection import mutual_info_regression
import sys
import multiprocessing as mp
from time import gmtime, strftime
sys.path.append('/cluster/tufts/levinlab/rellis01/calcium/varley')
from varley.local_mi import local_total_correlation
from tqdm import tqdm
from joblib import Parallel, delayed

'''
Mutual information calculation for calcium imaging data. 
The mutual information between two random variables is a measure of the mutual dependence between the two variables.
The mutual information between two vectors is calculated using the mutual_info_regression function from sklearn.
The mutual information between two vectors is calculated using the local_total_correlation function from varley.
Arguments:
    root (str): Path to the Suite2P output directory.
    mi_type (str): Type of mutual information calculation, 'global' or 'local'.
    overwrite (str): Whether to overwrite existing files, 'True' or 'False'.
Returns:
    None. Saves the mutual information matrix to a file named "mut_info_matrix.npy".
'''

def global_mi(data, sdir):

    """
    Calculate mutual information between pairs of vectors using parallel processing.

    Args:
        data (ndarray): Input data, a 2D array where each row represents a vector.

    Returns:
        None. Saves the mutual information matrix to a file named "mut_info_matrix.npy".
    """

    # create a square matrix to store the mutual information values
    n = len(data)
    mi_matrix = np.zeros((n, n))

    results = Parallel(n_jobs=-1, verbose=51)(
        delayed(mutual_info_regression)(
            data[i].reshape(-1, 1), data[j], n_neighbors=5, random_state=0
        ) for i in range(n) for j in range(i+1, n)
    )

    # Store the results in the matrix
    idx = 0
    for i in range(n):
        for j in range(i+1, n):
            mi_matrix[i, j] = results[idx]
            mi_matrix[j, i] = results[idx]
            idx += 1

    # save the mutual information matrix to a file
    filename = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F_mut_info_matrix.npy')
    np.save(filename, mi_matrix)

def local_total_correlation_wrapper(data):
    return local_total_correlation(data)

def local_mi(data, sdir):
    """
    Calculate local mutual information between pairs of vectors using parallel processing.

    Args:
        data (ndarray): Input data, a 2D array where each row represents a vector.

    Returns:
        None. Saves the local mutual information matrices to separate files in chunks.
    """
    n = len(data)
    mi_matrix = np.zeros((n, n, data.shape[1]))

    # convert data to float64 (required for cython function)
    data = data.astype(np.float64)

    # calculate the mutual information between all pairs of vectors and store in the matrix
    print('starting loop')
    results = Parallel(n_jobs=-1, verbose=51)(delayed(local_total_correlation_wrapper)(data[[i, j]]) for i in range(n) for j in range(i+1, n))

    # Store the results in the matrix
    idx = 0
    for i in range(n):
        for j in range(i+1, n):
            mi_matrix[i, j] = results[idx]
            mi_matrix[j, i] = results[idx]
            idx += 1
    
    # Save data
    filename = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F_local_mut_info_matrix.npy')
    np.save(filename, mi_matrix)

if __name__ == '__main__':
    # Define the path to the Suite2P output
    root = sys.argv[1]
    print(root)

    # type of mutual information calculation
    mi_type = sys.argv[2] # 'local' or 'global'
    print(mi_type)

    # whether to overwrite existing files
    overwrite = sys.argv[3] # 'True' or 'False' for overwriting existing files

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
        if os.path.isfile(os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F.npy')):
            # initialize filename
            if mi_type == 'global':
                filename = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F_mut_info_matrix.npy')
            elif mi_type == 'local':
                filename = os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F_local_mut_info_matrix.npy')

            # check if the file already exists and overwrite is set to False
            if os.path.isfile(filename) and not overwrite:
                print(f'{filename} already exists')
            # otherwise, run the mutual information calculation
            else:
                print(f'Running {mi_type} mutual information calculation on {sdir}\n')
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

                # Load data and remove first 1000 frames (lots of photobleaching)
                F = np.load(os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'F.npy'))
                iscell = np.load(os.path.join(sdir, 'bigtiffs', 'suite2p', 'plane0', 'iscell.npy'))   
                F = F[iscell[:, 0] == 1]
                F = F[:, 1000:6000]

                if mi_type == 'global':
                    global_mi(F, sdir)
                elif mi_type == 'local':
                    local_mi(F, sdir)

                print(f'{sdir} saved')
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))  
