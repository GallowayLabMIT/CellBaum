from typing import Dict, List
import numpy as np
import pandas as pd
from PIL import Image
import scipy.ndimage
from pathlib import Path
import os
import re
import shutil

def get_fval(image_file:Path)->int:
    im = Image.open(image_file).convert("L")
    im_array = np.array(im)
    weighting = np.array([[0,0,0], [0, -1, 1], [0,0,0]])
    corr_array = scipy.ndimage.correlate(im_array, weighting)
    val = np.sum(np.square(corr_array))
    return(val)

def get_bestz(image_list:List[Path])->Path:
    valcomp:Dict[int,Path] = {}
    for points in image_list:
        valcomp[get_fval(points)] = points
    best_file = valcomp[max(valcomp.keys())]
    return best_file

def find_focus(bigfold, outputfold, image_regex, wellops, log_filename = None):
    bigfold = Path(bigfold)
    outputfold = Path(outputfold)
    #image_regex = re.compile(r"""(?P<prefix>.*)_(?P<time>T\d{4})_(?P<well>XY\d{2})_(?P<position>\d{5})_Z(?P<stack>.{3})_(?P<channel>.*)\.tif""", re.VERBOSE)
    z_num_used = {}
    for time in sorted(next(os.walk(bigfold))[1]):
        Path.mkdir(outputfold/time, parents = True, exist_ok=True)
        if len(wellops) > 1:
            for wellname in wellops:
                zcheck = Path(bigfold/time).glob("*"+wellname+".tif")
                best_z = get_bestz(zcheck)
                z_num = re.match(image_regex, best_z.name).group('stack')
                pos_num = re.match(image_regex, best_z.name).group('position')
                z_num_used[best_z.name] = z_num
                for other_im in Path(bigfold/time).glob("*.tif"):
                    if (z_num == re.match(image_regex, other_im.name).group('stack')) and (wellname == re.match(image_regex, other_im.name).group('channel')):
                        naming = re.sub("_Z(?P<stack>.{3})", "", other_im.name)
                        shutil.copy(other_im, outputfold/time/naming)
        else:
            zcheck = Path(bigfold/time).glob("*"+wellops[0]+".tif")
            best_z = get_bestz(zcheck)
            z_num = re.match(image_regex, best_z.name).group('stack')
            pos_num = re.match(image_regex, best_z.name).group('position')
            z_num_used[best_z.name] = z_num
            for other_im in Path(bigfold/time).glob("*.tif"):
                if (z_num == re.match(image_regex, other_im.name).group('stack')):
                    naming = re.sub("_Z(?P<stack>.{3})", "", other_im.name)
                    shutil.copy(other_im, outputfold/time/naming)
    print(z_num_used)
'''
#given folder of wells
channels = ["CH2", "CH3", "CH4", "Overlay"]
#channels = ["CH2"]
#image_reg = re.compile(r"""(?P<prefix>.*)_(?P<time>T\d{4})_(?P<well>XY\d{2})_(?P<position>\d{5})_Z(?P<stack>.{3})_(?P<channel>.*)\.tif""", re.VERBOSE)
output = Path("/Users/ConradOakes/CellBaum/testoutput/XY01")
bigfolder = Path("/Users/ConradOakes/CellBaum/test/2022.01.26-test/XY01")
find_focus(bigfolder, output, channels)

z_folder = Path("/Users/ConradOakes/CellBaum/test/images").glob("*.tif")
print(get_bestz(z_folder))
'''