#!/usr/bin/env python
# coding: utf-8

# This script takes the non-zero mean of every channel of
# a mass corrected image, a filtered image, and their 
# difference. The results are saved to a csv file.
#
# The script should be placed in a folder containing 
# subfolders named "MassCorrectedImages" and
# "FilteredImages". These folders should contain the 
# corresponding image types.
#
# Author: Austin Edwards (austin.edwards@ucsf.edu)

import numpy as np
import pandas as pd
import imageio
import exifread
import pathlib

# Returns mean of all pixels that have a nonzero value
def nonzero_mean(image):
    return image[np.nonzero(image)].mean()

# Opens the tiff file
def open_tiff(file_name):
    image = imageio.mimread(file_name, multifile=True)
    return image

# Gets the channels from the tags
def get_tags(file_name, num_images):
    f = open(file_name, 'rb')
    tags = exifread.process_file(f)
    channel_list = [str(tags['Image PageName']), str(tags['Thumbnail PageName'])]
    for n in range(2, num_images):
        channel_list.append(str(tags['IFD ' + str(n) + ' PageName']))

    return channel_list

# Set paths
datadir = pathlib.Path("./Images")

filtereddir = pathlib.Path(datadir, "FilteredImages")
masscorrectdir = pathlib.Path(datadir, "MassCorrectedImages")

diffdir = pathlib.Path(datadir, "DifferenceImages")
if not diffdir.exists():
    diffdir.mkdir()

# Match image pairs

pairs = []

for masscorrectpartner in masscorrectdir.iterdir():
    
    filterpartner = pathlib.Path(filtereddir, masscorrectpartner.stem + "-Filtered.tiff")
    
    if filterpartner.exists():
        pairs.append([masscorrectpartner, filterpartner])

for pair in pairs:
    
    experiment = pair[0].name[:pair[0].name.find('MassCorrected')-1]
    print("Analyzing " + experiment)
    mc_image = open_tiff(pair[0])
    f_image = open_tiff(pair[1])
    
    mc_tags = get_tags(pair[0], len(mc_image))
    f_tags = get_tags(pair[1], len(f_image))
    
    channel_name = []
    mc_mean = []
    f_mean = []
    diff_mean = []
    ratio = []
    
    for index, channel, in enumerate(mc_tags):
        
        diff_image = mc_image[index] - f_image[index]
        
        channel_name.append( channel )
        mc_mean.append( nonzero_mean(mc_image[index]) )
        fm = nonzero_mean(f_image[index])
        f_mean.append(fm)
        dm = nonzero_mean(diff_image)
        diff_mean.append(dm)
        ratio.append(fm/dm)
        
    data = {'Channel Name':mc_tags, 
            'Mass Corrected Nonzero Mean': mc_mean, 
            'Filtered Nonzero Mean': f_mean, 
            'Difference Nonzero Mean': diff_mean,
            'Filtered to Difference Ratio': ratio}
    
    df = pd.DataFrame(data)
  
    df.to_csv(str(pathlib.Path(datadir, experiment + ".csv" )),index=False)



