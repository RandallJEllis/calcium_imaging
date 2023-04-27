import os
from tif_to_video import *
import sys
import argparse

# Create an argument parser
parser = argparse.ArgumentParser()

# Add a positional argument
parser.add_argument('filepath', help='Filepath to experiment(s) to create bigTIFF videos from.')

# Add an optional argument with a default value
parser.add_argument('--output', '-o',  help='Output filename.')

# Add an optional argument with a choice of values
parser.add_argument('--batch', '-b', choices=['y', 'n'], default='y', help='Default: y. Find subdirectories with "5min"? (y/n). If no, will treat filepath as a single directory to create a bigTIFF video.')

parser.add_argument('--overwrite', '-w', choices=['y', 'n'], default='n', help='Default: n. Overwrite bigtiffs directory? (y/n). If no, will skip directory.')

# Parse the command line arguments
args = parser.parse_args()

# Print out the arguments
print('File path:', args.filepath)
print('Output filename:', args.output)
print('Batch:', args.batch)

# define the path to the input directory
input_path = args.filepath

# define the output filename
output_filename = args.output

# define whether to overwrite the bigtiffs directory
if args.overwrite == 'y':
    overwrite = True
else:
    overwrite = False

# define whether batch processing or not
if args.batch == 'y':
    batch = True
else:
    batch = False

if batch == True:
    print('batch processing')
    # iterate over directories with '5minTL' in the name
    for dir in os.listdir(input_path):
        if '5min' in dir:
            # define the path to the directory
            dir_path = os.path.join(input_path, dir)
            print(dir_path)
            # check if the bigtiffs directory already exists
            if os.path.exists(os.path.join(dir_path, 'bigtiffs')):
                # if overwrite is True, generate the bigtiffs directory
                if overwrite == True:
                    print('overwriting bigtiffs directory')
                    tif_to_video(dir_path, output_filename)
                # if overwrite is False, skip the directory
                else:
                    print('bigtiffs directory already exists')
                    continue
            else: 
                tif_to_video(dir_path, output_filename)
else:
    print('single directory processing')
    tif_to_video(input_path, output_filename)
                
