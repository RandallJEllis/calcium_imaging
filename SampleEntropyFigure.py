import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import sys

def colorize_values(values, value_range, cmap_name='viridis'):
    """
    Colorizes a list of continuous values over a given range using a selected gradient colormap.

    Args:
        values (list or numpy.ndarray): List of continuous values.
        value_range (tuple): Range of values (minimum and maximum) for normalization.
        cmap_name (str): Name of the colormap to use (default: 'viridis').

    Returns:
        list: List of RGBA color tuples corresponding to each value.
    """
    # Normalize values between 0 and 1
    normalized_values = (np.array(values) - value_range[0]) / (value_range[1] - value_range[0])

    # Create the colormap
    cmap = plt.cm.get_cmap(cmap_name)

    # Get the color for each normalized value
    colors = cmap(normalized_values)

    # Convert colors to RGBA tuples
    rgba_colors = [tuple(color) for color in colors]

    # Create a figure to display the colorbar
    fig, ax = plt.subplots(figsize=(6, 1))
    fig.subplots_adjust(bottom=0.5)

    # Set the colormap as a colorbar
    norm = plt.Normalize(*value_range)
    cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal')
    cbar.set_label('Sample Entropy ColorBar')
    # cbar.title("")

    # Show the figure
    # plt.savefig('/cluster/tufts/levinlab/shansa01/CalciumSignaling/figures/SampleEntropyColorBar.png')
    plt.show()
    return rgba_colors

if __name__ == "__main__":

    # Example input: /cluster/tufts/levinlab/shansa01/CalciumSignaling/HH_cellpose_model_training/HH/1_5minTL.2023-02-14-19-29-03
    # Example usage: python CalciumSignaling/scripts/SampleEntropyFigure.py /cluster/tufts/levinlab/shansa01/CalciumSignaling/HH_cellpose_model_training/HH/1_5minTL.2023-02-14-19-29-03
    experiment_path_input = sys.argv[1]
    data_dir = f'{experiment_path_input}/bigtiffs/suite2p/plane0/'

    F = np.load(f'{data_dir}F.npy', allow_pickle=True)
    Fneu = np.load(f'{data_dir}Fneu.npy', allow_pickle=True)
    spks = np.load(f'{data_dir}spks.npy', allow_pickle=True)
    stat = np.load(f'{data_dir}stat.npy', allow_pickle=True)
    iscell = np.load(f'{data_dir}iscell.npy', allow_pickle=True)
    # Note, need 8gb memory to run the below
    ops =  np.load(f'{data_dir}ops.npy', allow_pickle=True)
    ops = ops.item()

    stat_cells = stat[iscell[:,0]==1]
    loaded_sampens = np.load('/cluster/tufts/levinlab/shansa01/CalciumSignaling/sampen_expers/all_sampens.npy')

    # Assuming you have the arrays of x and y coordinates
    x_coordinates = [x['xpix'] for x in stat_cells]  # Array of x-coordinates for each cell
    y_coordinates = [y['ypix'] for y in stat_cells]  # Array of y-coordinates for each cell
    sampens = loaded_sampens
    rgba_colors = colorize_values(sampens, (0, 2.1))

    # Create a new figure and axes
    fig, ax = plt.subplots()

    # Iterate over each cell's coordinates and plot them as points
    for x, y, clr in zip(x_coordinates, y_coordinates, rgba_colors):
        ax.plot(x, y, 'o', color=clr)

    # Set the aspect ratio to equal, so the cells are not distorted
    ax.set_aspect('equal')

    # heatmap = ax.imshow(sampens, cmap='viridis', aspect='auto')
    # cbar = fig.colorbar(heatmap)

    # Show the plot
    # plt.savefig('/cluster/tufts/levinlab/shansa01/CalciumSignaling/figures/SampleEntropyCells.png')
    plt.show()