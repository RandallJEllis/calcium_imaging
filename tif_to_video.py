import cv2
import os
import sys
import numpy as np
from tqdm import tqdm
from PIL import Image
from tifffile import TiffWriter

def tif_to_video(input_path, output_filename, chunk=None, downsample_resolution=None):
    
    """Converts a series of TIFF images into a video file and exports each chunk of TIFFs separately in bigTIFF format.
    Also exports an Avi file.
    
    Args:
        input_path (str): The path to the directory containing the TIFF images.
        output_filename (str): The name of the output video file (without the file extension).
        chunk (int, optional): The number of TIFF files per chunk. If specified, the TIFF files will be split into
            chunks and each chunk will be saved as a separate bigTIFF file. Defaults to None (i.e., all TIFF files 
            will be processed together).
        downsample_resolution (tuple, optional): A tuple of integers (width, height) specifying the desired resolution 
            to downsample each TIFF image to. If specified, each TIFF image will be downsampled to the given resolution 
            before being added to the video file. Defaults to None (i.e., no downsampling will be performed).
    
    Returns:
        None
        
    Raises:
        None
    
    """

    # List of TIF files
    tif_files = [f for f in os.listdir(input_path) if f.endswith('.TIF')]
    if len(tif_files)==0:
        print('No TIFF files found in the specified directory.')
        sys.exit()

    # Sort image filenames by number following 'p' in filename
    framenums = []
    for tif_file in tif_files:
        p_idx = tif_file.find('p')
        underscore_idx = tif_file[p_idx:].find('_')
        framenum = tif_file[p_idx+1:p_idx+underscore_idx]
        framenums.append(int(framenum))
    
    # order filenames in a list
    tif_files = [tif_file for _, tif_file in sorted(zip(framenums, tif_files))]
    
    # take the first 5 minutes of data
    tif_files = tif_files[:6000]
    
    if not os.path.exists(f'{input_path}/bigtiffs'):
        os.makedirs(f'{input_path}/bigtiffs')

    # Split the TIF files into chunks if a chunk size is specified
    if chunk:
        tif_files_chunks = [tif_files[i:i+chunk] for i in range(0, len(tif_files), chunk)]
    else:
        tif_files_chunks = [tif_files]

    for i, tif_files_chunk in enumerate(tif_files_chunks):
        # Initialize an empty list to hold the image data for the chunk
        arr_list = []

        # Iterate over the TIF files in the chunk, import and add each TIF frame to arr_list
        for tif_file in tqdm(tif_files_chunk, desc=f'Chunk {i+1}/{len(tif_files_chunks)}'):
            img = cv2.imread(os.path.join(input_path, tif_file), 0) # read in grayscale
            if downsample_resolution is not None:
                img = cv2.resize(img, downsample_resolution)
            img = img[...,None] # add third dimension (i.e., frame)
            arr_list.append(img)

        # concatenate frames into numpy array
        tiff_arr = np.concatenate(arr_list, axis=2)

        # export numpy array in bigTIFF format at 20 FPS
        with TiffWriter(f'{input_path}/bigtiffs/{output_filename}_chunk{i+1}.tif', bigtiff=True) as tif:
            for frame in np.transpose(tiff_arr,(2,0,1)):
                tif.write(frame, metadata={'fps':20.0})

    ### AVI ###
    #Define the output video file name and format
    # output_file = f'{output_filename}.avi'

    # # Define the FourCC code, which specifies the video codec
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    # # Get the dimensions of the first TIF file
    # img = cv2.imread(os.path.join(input_path, tif_files[0]))
    # height, width = img.shape[:2]

    # if not os.path.exists(f'{input_path}/avi'):
    #     os.makedirs(f'{input_path}/avi')
    # # Initialize the VideoWriter object, specifying that the images are not in color format
    # out = cv2.VideoWriter(f'{input_path}/avi/{output_file}', fourcc, 20.0, (width, height), isColor=False)

    
    # #Iterate over the TIF files, normalize, and add each frame to that video
    # for tif_file in tqdm(tif_files):
    #     img = cv2.imread(os.path.join(input_path, tif_file), -1)

    #     # KEY STEP - normalize all images using 4096 (max intensity for 16-bit images), multiply by 255 (max for 8-bit), and convert to 8-bit
    #     img = ((img/4096) * 255).astype(np.uint8)

    #     #output image
    #     out.write(img)

    # # Release the VideoWriter object
    # out.release()


