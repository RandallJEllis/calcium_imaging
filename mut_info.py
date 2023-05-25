import numpy as np
import os
from sklearn.feature_selection import mutual_info_regression
import sys
import multiprocessing as mp
from time import gmtime, strftime
from varley.local_mi import local_total_correlation
from tqdm import tqdm

'''
Calculate mutual information between all pairs of vectors in a directory tree of cell spike data 
and store the resulting mutual information matrix.

Args:
    root (str): the path to the root directory of the cell spike data.

The script searches through all subdirectories in the given root directory for subdirectories 
containing the string '5min'. For each of these subdirectories, it loads the cell spike data from
the file 'cell_spks.npy' in the subdirectory 'bigtiffs/suite2p/plane0', calculates the mutual 
information between all pairs of vectors using mutual_info_regression() from the scikit-learn 
package, and saves the resulting mutual information matrix as a NumPy binary file 
'mut_info_matrix.npy' in the same subdirectory.

Note that the mutual information values are only calculated for a subset of the time series data 
(from time steps 1000 to 6000), and that the script skips over subdirectories for which the mutual
information matrix file already exists.

Returns:
    None.
'''

def mi_parallel(data):
    # create a square matrix to store the mutual information values
    n = len(data)
    mi_matrix = np.zeros((n, n))

    # calculate the mutual information between all pairs of vectors and store in the matrix
    with multiprocessing.Pool() as pool:
        futures = []
        for i in range(n):
            for j in range(i+1, n):
                if i == j:
                    continue
                futures.append(pool.apply_async(
                    mutual_info_regression, (data[i].reshape(-1, 1), data[j]),
                    {'n_neighbors': 5, 'random_state': 0}))
        for i, f in enumerate(tqdm(futures, total=len(futures))):
            mi_matrix[i//n, i%n] = f.get()
            mi_matrix[i%n, i//n] = mi_matrix[i//n, i%n]

    # save the mutual information matrix to a file
    np.save("mut_info_matrix.npy", mi_matrix)



def local_mi(data):
    n = len(data)
    mi_matrix = np.zeros((n, n, data.shape[1]))

    # convert data to float64 (required for cython function)
    data = data.astype(np.float64)

    # Chunk size for saving
    chunk_size = 100

    # calculate the mutual information between all pairs of vectors and store in the matrix
    with mp.Pool(mp.cpu_count()) as pool:
        futures = []
        for i in range(n):
            print(f'Neuron {i} out of {n}, {strftime("%Y-%m-%d %H:%M:%S", gmtime())}')
            for j in range(i+1, n):
                if i == j:
                    continue
                dpass = data[[i,j]]
                futures.append(pool.apply_async(local_total_correlation, args=(dpass,)))
        
        # Save mi_matrix in smaller chunks
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            chunk = futures[start:end]
            for i, f in enumerate(chunk):
                mi_matrix[start:end, i] = f.get()
                mi_matrix[i, start:end] = mi_matrix[start:end, i]

            # Save the chunk to a file
            filename = os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', f'local_mut_info_matrix_chunk_{start}_{end}.npy')
            np.save(filename, mi_matrix[start:end])


# Define the path to the Suite2P output
root = sys.argv[1]
print(root)

mi_type = sys.argv[2] # 'local' or 'global'
print(mi_type)

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
for dir in subdirectories:
    print(dir)
    # check if 'cell_spks.npy' exists in the directory
    if os.path.isfile(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'cell_spks.npy')):
        # initialize filename
        if mi_type == 'global':
            filename = os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'mut_info_matrix.npy')
        elif mi_type == 'local':
            filename = os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'local_mut_info_matrix.npy')
        if os.path.isfile(filename) and not overwrite:
            print(f'{filename} already exists')
        else:
            print(f'Running {mi_type} mutual information calculation on {dir}\n')
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

            cell_spks = np.load(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'cell_spks.npy'))
            cell_spks = cell_spks[:, 1000:6000]

            if mi_type == 'global':
                mi_parallel(cell_spks)
            elif mi_type == 'local':
                local_mi(cell_spks)

            print(f'{filename} saved')
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))