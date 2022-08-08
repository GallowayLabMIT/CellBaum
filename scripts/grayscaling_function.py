from typing import Dict, List, Literal, Pattern, Union
from PIL import Image
from pathlib import Path
import numpy as np
import os
import re

def image_conversion(image_path:Path, output_path:Path, conversion:Union[List[float], Literal['avg'], Literal['max']])->None:
    """
    Takes an image, converts it to grayscale following the specified conversion pattern,
    then saves the image
    Parameters
    ----------
    image_path: Path
        The path to the specific image
    output_path: Path
        The path to the output folder where the image is to be saved
    conversion: Dict or str
        The conversion method, either maximum across all channels, the average of all channels, 
        or a user defined ratio
    Returns
    -------
    """
    im = Image.open(image_path)
    im_array = np.array(im)
    if np.ndim(im_array) == 2:
        correct_im = im_array
        final_im = Image.fromarray((correct_im).astype('u2'))
    else:
        if conversion == 'max':
            correct_im = np.amax(im_array, axis = 2)
            final_im = Image.fromarray((correct_im))
        elif conversion == 'avg':
            correct_im = np.mean(im_array, axis = 2)
            final_im = Image.fromarray((correct_im*255).astype('u2'))
        else:
            Rval = im_array[:,:,0]*conversion[0]
            Gval = im_array[:,:,1]*conversion[1]
            Bval = im_array[:,:,2]*conversion[2]
            correct_im = Rval+ Gval+ Bval
            final_im = Image.fromarray((correct_im))
    final_im.save(str(output_path/image_path.name))


def grayscale_folder(image_dir:Path, outputfold:Path, regex:Pattern, conversion:Dict)->None:
    """
    Takes a folder of images, converts them to grayscale, 
    and then creates a new folder with these images
    Parameters
    ----------
    image_dir: Path
        The path to the images that are being analyzed
    outputfold: Path
        The path to the output folder for the images found by this analysis
    regex: Regular Expression Pattern
        The regular expression that matches each image in the image_dir
    conversion: Dict
        The dictionary matching channels to desired conversions to grayscale
    log_filename: Path
        The path to the logfile being generated
    Returns 
    -------
    """
    image_dir = Path(image_dir)
    outputfold = Path(outputfold)
    # for each time point stored in the folder
    for time in sorted(next(os.walk(image_dir))[1]):
        Path.mkdir(outputfold/time, parents = True, exist_ok=True)
        for im_name in Path(image_dir/time).glob("*.tif"):
            chan = re.match(regex, im_name.name).group('channel')
            image_conversion(im_name, outputfold/time, conversion[chan])

'''
output = Path("/Users/ConradOakes/CellBaum/testgrayresult/XY11")
bigfolder = Path("/Users/ConradOakes/CellBaum/testgray/XY11")
image_reg = re.compile(r"""(?P<prefix>.*)_(?P<time>T\d{4})_(?P<well>XY\d{2})_Z(?P<stack>\d{3})_(?P<channel>.*)\.tif""", re.VERBOSE)
conversion_dict = {"CH1": [0, 0, 1], "CH2": [0, 1, 0], "CH3": [0, 0, 1], "CH4": 'max', "Overlay": 'avg'}
grayscale_folder(bigfolder, output, image_reg, conversion_dict)
'''