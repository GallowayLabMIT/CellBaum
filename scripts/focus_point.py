from typing import Dict, List, Pattern
import numpy as np
import pandas as pd
from PIL import Image
import scipy.ndimage
from pathlib import Path
import os
import re
import shutil
import csv

def get_fval(image_file:Path)->int:
    """
    Runs a correlation on the provided image and returns a value that 
    correlates with how in focus the image is
    Parameters
    ----------
    image_file: Path
        The path to the image file being analyzed
    Returns
    -------
    An integer that is the result of the correlation"""
    # opens image as array
    im = Image.open(image_file)
    im_array = np.array(im)
    # runs the correlation
    weighting = np.array([[0,0,0], [0, -1, 1], [0,0,0]])
    corr_array = scipy.ndimage.correlate(im_array, weighting)
    # sums the squared values
    val = np.sum(np.square(corr_array))
    return(val)

def get_bestz(image_list:List[Path])->Path:
    """
    Given a folder of images, finds the most in focus 
    using the get_fval function
    Parameters
    ----------
    image_list: a list of Paths 
        A list of the paths to the images of a zstack
    Returns
    -------
    The path to the image that was found to be the most in focus """
    valcomp:Dict[int,Path] = {}
    for points in image_list:
        valcomp[get_fval(points)] = points
    best_file = valcomp[max(valcomp.keys())]
    return best_file

def find_focus(image_dir:Path, outputfold:Path, image_regex:Pattern, channels:List[str])->None:
    """
    Takes a folder of z-stacked images, finds the most in focus for each position, 
    and then creates a new folder with only the in focus images
    Parameters
    ----------
    image_dir: Path
        The path to the images that are being analyzed
    outputfold: Path
        The path to the output folder for the images found by this analysis
    image_regex: Regular Expression Pattern
        The regular expression that matches each image in the image_dir
    channels: List of strs
        The list of channels in the image set. Either a singular channel, whose z position is used for the reminder,
        or a list of all channels to use unique z positions for each
    log_filename: Path
        The path to the logfile being generated
    Returns 
    -------
    """
    image_dir = Path(image_dir)
    outputfold = Path(outputfold)
    z_num_used = {}
    # for each time point stored in the folder
    for time in sorted(next(os.walk(image_dir))[1]):
        Path.mkdir(outputfold/time, parents = True, exist_ok=True)
        # if finding individual focus points for each channel
        if len(channels) > 1:
            for channame in channels:
                # find all possible images
                zcheck = Path(image_dir/time).glob("*"+channame+".tif")
                # get the best focus point
                best_z = get_bestz(zcheck)
                z_num = re.match(image_regex, best_z.name).group('stack')
                pos_num = re.match(image_regex, best_z.name).group('position')
                z_num_used[best_z.name] = z_num
                # use the focus point to find the other images with that z value and save them
                for other_im in Path(image_dir/time).glob("*.tif"):
                    if (z_num == re.match(image_regex, other_im.name).group('stack')) and (channame == re.match(image_regex, other_im.name).group('channel')):
                        naming = re.sub("_Z(?P<stack>.{3})", "", other_im.name)
                        shutil.copy(other_im, outputfold/time/naming)
        else:
            # find all possible images in the primary channel
            zcheck = Path(image_dir/time).glob("*"+channels[0]+".tif")
            # get the best focus point
            best_z = get_bestz(zcheck)
            z_num = re.match(image_regex, best_z.name).group('stack')
            pos_num = re.match(image_regex, best_z.name).group('position')
            z_num_used[best_z.name] = z_num
            # use the focus point to find the other images with that z value and save them
            for other_im in Path(image_dir/time).glob("*.tif"):
                if (z_num == re.match(image_regex, other_im.name).group('stack')):
                    naming = re.sub("_Z(?P<stack>.{3})", "", other_im.name)
                    shutil.copy(other_im, outputfold/time/naming)
    # creates a csv with the z values used
    f = open(outputfold/'Znum_used.csv','w')
    w = csv.DictWriter(f,z_num_used.values())
    w.writeheader()
    w.writerow(z_num_used.keys())
    f.close()
'''
#given folder of wells
channels = ["CH1", "CH4", "Overlay"]
#channels = ["CH2"]
image_reg = re.compile(r"""(?P<prefix>.*)_(?P<time>T\d{4})_(?P<well>XY\d{2})_(?P<position>\d{5})_Z(?P<stack>.{3})_(?P<channel>.*)\.tif""", re.VERBOSE)
output = Path("/Users/ConradOakes/CellBaum/testoutput/XY01")
bigfolder = Path("/Users/ConradOakes/CellBaum/test/alttest/XY01")
find_focus(bigfolder, output, image_reg, channels)

z_folder = Path("/Users/ConradOakes/CellBaum/test/images").glob("*.tif")
print(get_bestz(z_folder))
'''