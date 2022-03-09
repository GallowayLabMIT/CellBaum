#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 23:48:30 2021

@author: ConradOakes
"""
import subprocess
import sys
import os
from pathlib import Path
import contextlib
import itertools
import re
from typing import List, Literal, Optional, Pattern


def java_quote(input_str:str)->str:
    if " " in input_str:
        return f"'{input_str}'"
    return input_str

"""
Takes a regular expression describing the images and generates 
a list of namekeys for use by the stitching function.
Parameters
----------
example_name: str
    A string corresponding to an image in the dataset
channels: list of strings 
    A list of the channels that will be stitched
regex: Regular Expression Pattern
    The regular expression matching the dataset
focused: Boolean 
    Describing if the focus_point function is part of the pipeline (defalut = False)
corrected: 
    The list of channels corrected by img_processing, if any (defalut = [])
Returns
-------
The list of strings used as namekeys by the stitching function
"""
def get_namekeys(example_name:str, channels:List[str], regex:Pattern[str], focused:bool = False, corrected:List[str] = [])->List[str]:
    if re.match(regex, example_name):
        namekeys:List[str] = []
        # for each channel
        for chan in channels:
            # shift the regex into a namekey
            new_reg = re.sub("_(?P<time>T\d{4})", "_time", example_name)
            new_reg = re.sub("_(?P<well>XY\d{2})", "_well", new_reg)
            new_reg = re.sub("_(?P<position>\d{5})", "_000{pp}", new_reg)
            # use different name for corrected channels
            if chan in corrected:
                new_reg = re.sub("_Z(?P<stack>.{3})_(?P<channel>.*).tif", "_Z_"+chan+"_threshold.tiff", new_reg)
            else:
                new_reg = re.sub("_Z(?P<stack>.{3})_(?P<channel>.*).tif", "_Z_"+chan+".tif", new_reg)
            # eliminate the z position for focused datasets
            if focused:
                new_reg = re.sub("_Z", "", new_reg)
            else:
                new_reg = re.sub("_Z", "_Z{ttt}", new_reg)
            namekeys += [new_reg]
        return namekeys
    else:
        raise RuntimeError("Explosion; Regular Expression Pattern does not match the example image")

"""
Uses MIST to stitch together sets of images. Requires the Fiji application to 
be installed and for it to have added the NIST plugin. 
Parameters
----------
fiji_dir: Path
    The path to the Fiji app
java_dir: Path
    The path to the Java app
image_dir: Path
    Path to the folder with the images
name_keys: List of strings
    A list of the regular expressions for the file names of each channel. Requires a position {p} argument. 
    If z_extent exists, also needs a z {t} argument
prefix: List of strings
    The names of each channel (for final output); should in the same order as name_keys
template: Int
    The index of the channel in name_keys/prefix that is used as a stitching template
grid_width: Int
    Expected width of stitched grid in images
grid_height: Int
    Expected height of stitched grid in images
output: Path
    The path to the output folder for the images created by the stitcher
z_extent: (optional) List of strings
    An optional list of a minimum and maximum z value (defalut = None)
log_filename: (optional) Path
    Path to the log file (default = None)
order: str
    The order of the positions in the {p} of name_keys (default = SEQUENTIAL)
scope_path: str
    The microscopes path (default = HORIZONTALCONTINUOUS)
Returns
-------
An int (1 or 0) designating successful completion of the command line task
"""
def stitching(fiji_dir:Path, java_dir:Path, image_dir:Path, name_keys:List[str], prefix:List[str], template:int, grid_width:int, grid_height:int,
              output:Path, z_extent:Optional[List[int]] = None, log_filename:Optional[Path] = None, order:Literal['SEQUENTIAL','ROWCOLUMN'] = "SEQUENTIAL", 
              scope_path:Literal['HORIZONTALCONTINUOUS','HORIZONTALCOMBING','VERTICALCONTINUOUS','VERTICALCOMBING'] = "HORIZONTALCONTINUOUS")->int:
    if z_extent is None:
        z_list = '0'
    else:
        z_list = f"{z_extent[0]}-{z_extent[1]}"
    output = Path(output)
    image_dir = Path(image_dir)
    well = os.path.basename(os.path.normpath(image_dir))
    old_dir = os.getcwd()

    # Setup Java args properly
    jar_paths = ["plugins/MIST_.jar", "jars/*"]
    if sys.platform.startswith('win32'):
        separator = ';'
    else:
        separator = ':'
    classpath = separator.join(jar_paths)
    java_args = [java_dir, '-cp', classpath, 'gov.nist.isg.mist.MISTMain']

    if log_filename is None:
        @contextlib.contextmanager
        def dummy():
            yield True

        logfile = dummy()
        extra_args = {}
    else:
        logfile = open(log_filename, 'w')
        extra_args = {'stdout':logfile, 'stderr':logfile}


    BASE_ARGS = {
                    "--gridWidth": "placeholder",
                    "--gridHeight": "placeholder",
                    "--startTile": '1',
                    "--imageDir": "placeholder",
                    "--filenamePattern": "placeholder",
                    "--filenamePatternType": "placeholder",
                    "--gridOrigin": "UL",
                    "--assembleNoOverlap": 'False',
                    "--globalPositionsFile": '[]',
                    "--numberingPattern": "placeholder",
                    "--startRow": '0',
                    "--startCol": '0',
                    "--extentWidth": "placeholder",
                    "--extentHeight": "placeholder",
                    "--timeSlices": "placeholder",
                    "--isTimeSlicesEnabled": 'True' if z_extent is not None else 'False',
                    "--outputPath": "placeholder",
                    "--displayStitching": 'False',
                    "--outputFullImage": 'True',
                    "--outputMeta": 'True',
                    "--outputImgPyramid": 'False',
                    "--blendingMode": "OVERLAY",
                    "--blendingAlpha": "NaN",
                    "--outFilePrefix": "placeholder",
                    "--programType": "AUTO",
                    "--numCPUThreads": "8",
                    "--loadFFTWPlan": 'True',
                    "--saveFFTWPlan": 'True',
                    '--fftwPlanType': "MEASURE",
                    '--fftwLibraryName': "libfftw3",
                    '--fftwLibraryFilename': "libfftw3.dll",
                    '--planPath': "lib/fftw/fftPlans",
                    '--fftwLibraryPath': "lib/fftw",
                    '--stageRepeatability': '0',
                    '--horizontalOverlap': "NaN",
                    '--verticalOverlap': "NaN",
                    '--numFFTPeaks': '0',
                    '--overlapUncertainty': "NaN",
                    '--isUseDoublePrecision': 'False',
                    '--isUseBioFormats': 'False',
                    '--isSuppressModelWarningDialog': 'False',
                    '--isEnableCudaExceptions': 'False',
                    '--translationRefinementMethod': "SINGLE_HILL_CLIMB",
                    '--numTranslationRefinementStartPoints': '16',
                    '--headless': 'True',
                    '--logLevel': "MANDATORY",
                    '--debugLevel': "NONE"
    }


    with logfile:
        # for each time point folder in the given directory....
        dir_path = Path(image_dir)
        for image_set in dir_path.iterdir():
            if image_set.is_dir():
                #create the regular expression for each image in that folder
                t = os.path.basename(os.path.normpath(image_set))
                start_file = name_keys[template]
                start_file = start_file.replace('time', t)
                start_file = start_file.replace('well', well)
                #name the output file
                outfile = t+'_'+prefix[template]
                #switch to the java directory
                os.chdir(fiji_dir)
                args_dict = BASE_ARGS
                args_dict["--assembleFromMetadata"] = 'False'
                args_dict["--gridWidth"] = str(grid_width)
                args_dict["--gridHeight"] = str(grid_height)
                args_dict["--imageDir"] =  java_quote(str(image_set))
                args_dict["--filenamePattern"] = start_file
                args_dict["--filenamePatternType"]= order
                args_dict["--numberingPattern"]= scope_path
                args_dict["--startRow"]= '0'
                args_dict["--startCol"]= '0'
                args_dict["--extentWidth"]= str(grid_width)
                args_dict["--extentHeight"]= str(grid_height)
                args_dict["--timeSlices"]= z_list
                args_dict["--outputPath"]= str(output)
                args_dict["--outFilePrefix"]= outfile
                
                primary_args = list(itertools.chain.from_iterable([('{}'.format(k), v) for k,v in args_dict.items()]))
                final_args = java_args + primary_args
                #run NIST with arguments
                run_result = subprocess.run(final_args, **extra_args)

                #for each channel other than the template...
                for channel in range(len(prefix)):
                    if (channel) != template:
                        #set the name
                        channel_set =  name_keys[channel]
                        channel_set = channel_set.replace('time', t)
                        channel_set = channel_set.replace('well', well)
                        #create arguments assembling from the template channel's metadata
                        sec_dict = BASE_ARGS
                        sec_dict["--assembleFromMetadata"] = 'True'
                        sec_dict["--gridWidth"] = str(grid_width)
                        sec_dict["--gridHeight"] = str(grid_height)
                        sec_dict["--imageDir"] =  java_quote(str(image_dir/t))
                        sec_dict["--filenamePattern"] = channel_set
                        sec_dict["--filenamePatternType"]= order
                        sec_dict["--globalPositionsFile"]= java_quote(
                            str(output/(outfile+ 'global-positions-{t}.txt')) if z_extent is not None 
                            else str(output/(outfile + 'global-positions-0.txt')))
                        sec_dict["--numberingPattern"]= scope_path
                        sec_dict["--startRow"]= '0'
                        sec_dict["--startCol"]= '0'
                        sec_dict["--extentWidth"]= str(grid_width)
                        sec_dict["--extentHeight"]= str(grid_height)
                        sec_dict["--timeSlices"]= z_list
                        sec_dict["--outputPath"]= java_quote(str(output))
                        sec_dict["--outFilePrefix"]= t+ '_'+prefix[channel]
                        
                        secondary_args = list(itertools.chain.from_iterable([('{}'.format(k), v) for k,v in sec_dict.items()]))
                        final_args2 = java_args + secondary_args
                        #run NIST with new arguments
                        run_result = subprocess.run(final_args2, **extra_args)
        os.chdir(old_dir)
        return(run_result.returncode)

'''
#2021.01.18_10X_time_well_000{pp}_CH1.tif
channeles = ["CH2", "CH3", "CH4", "Overlay"]
image_reg = re.compile(r"""(?P<prefix>.*)_(?P<time>T\d{4})_(?P<well>XY\d{2})_(?P<position>\d{5})_Z(?P<stack>.{3})_(?P<channel>.*)\.tif""", re.VERBOSE)
example = '10X_T0001_XY01_00001_Z001_CH2.tif'
name_key = get_namekeys(example, channeles, image_reg, focused = True)
print(name_key)

fiji_loc = Path('/Applications/Fiji.app')
java_loc = Path('/Applications/Fiji.app/java/macosx/adoptopenjdk-8.jdk/jre/Contents/Home/bin/java')
data_dir = Path('/Users/ConradOakes/CellBaum/testing/XY01')
prefixes = ["CH2", "CH3", "CH4", "Overlay"]
main_chan = 1
output_dir = Path("/Users/ConradOakes/CellBaum/output/stitched/XY01")
log_dir = "/Users/ConradOakes/CellBaum/snakemake_logs/XY01stitching_log.txt"

stitching(fiji_dir = fiji_loc, java_dir = java_loc, image_dir = data_dir, name_keys = name_key, prefix = prefixes, template = main_chan,
              grid_width = 3, grid_height = 2, output = output_dir, log_filename=log_dir)
'''