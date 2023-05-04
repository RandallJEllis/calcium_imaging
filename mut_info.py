import numpy as np
import os
from sklearn.feature_selection import mutual_info_regression
import sys

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


def mi(data):
    # create a square matrix to store the mutual information values
    n = len(data)
    mi_matrix = np.zeros((n, n))

    # calculate the mutual information between all pairs of vectors and store in the matrix
    for i in range(n):
        for j in range(n):
            if i <= j:
                mi = mutual_info_regression(data[i].reshape(-1, 1)[1000:6000],
                                            data[j][1000:6000])
                mi_matrix[i, j] = mi
                mi_matrix[j, i] = mi

    # save the mutual information matrix to a file
    np.save("mut_info_matrix.npy", mi_matrix)


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
    # check if 'cell_spks.npy' exists in the directory
    if os.path.isfile(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'cell_spks.npy')):
        # check if 'cell_spks.npy' exists in the directory
        if os.path.isfile(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'mut_info_matrix.npy')):
            print('mut_info_matrix.npy already exists')
            continue
        else:
            print(f'Running mutual information calculation on {dir}')
            cell_spks = np.load(os.path.join(dir, 'bigtiffs', 'suite2p', 'plane0', 'cell_spks.npy'))
            mi(cell_spks)
            print('mut_info_matrix.npy saved')
    else:
        print('cell_spks.npy does not exist')
        continue