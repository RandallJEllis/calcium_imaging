# calcium_imaging
Tools to process calcium imaging data, including exporting images to videos, and analyzing videos via Suite2P 

The pipeline runs in the following order:

1. `create_bigtifs_multiple_folders.py` takes a filepath as input and calls `tif_to_video.py`, which takes .TIF images as input and exports TIF stacks in bigTIFF format
2. `suite2p_script.py` runs Suite2P on these bigTIFF stacks, and the outputs of Suite2p are all numpy arrays described (here)[https://suite2p.readthedocs.io/en/latest/outputs.html]. The most important of these outputs is `spks.npy`, which contains the final deconvolved time series of all regions of interest (ROIs; i.e., cells and non-cells). 
3. `subset_spks_cellROIs.py` searches for all `spks.npy` files and subsets the cell ROIs to produce `cell
