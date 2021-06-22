#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 23:48:30 2021

@author: ConradOakes
"""
import subprocess
import sys
import os
import sys
from pathlib import Path
import contextlib

"""
Uses NIST to stitch together sets of images. Requires the Fiji application to 
be installed and for it to have added the NIST plugin. 

fiji_dir: the path to the Fiji app
java_dir: the path to the Java app
template_dir: path to the folder with the template images
other_dir: path to the folder with other images
name_keys: a list of the regular expressions for the file names of each channel 
    (requires a position {p} and z {t} argument)
prefix: the names of each channel (for final output); should in the same order 
    as name_keys
template: the position in name_keys/prefix of the channel that is used as a 
    stitching template
output: the output directory
log_filename: name for log
order: order of the positions in the {p} of name_keys (default = SEQUENTIAL)
scope_path: the microscopes path (defalut = HORIZONTALCONTINUOUS)
z_list: number of z levels
"""
def stitching(fiji_dir, java_dir, image_dir, name_keys, prefix, template, grid_width, grid_height,
              output, z_min, z_max, log_filename = None, order = "SEQUENTIAL", 
              scope_path = "HORIZONTALCONTINUOUS"):
    z_list = f"{z_min}-{z_max}"
    output = Path(output)
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
        @contextmanager
        def dummy():
            yield True

        logfile = dummy()
        extra_args = {}
    else:
        logfile = open(log_filename, 'w')
        extra_args = {'stdout':logfile, 'stderr':logfile}

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
                #create arguments, accounting for spaces in the folder name
                if " " in str(image_set):
                    args_primary = [
                        "--gridWidth", str(grid_width),
                        "--gridHeight", str(grid_height),
                        "--startTile", '1',
                        "--imageDir", "'"+str(image_set)+"'",
                        "--filenamePattern", start_file,
                        "--filenamePatternType", order,
                        "--gridOrigin", "UL",
                        "--assembleFromMetadata", 'False',
                        "--assembleNoOverlap", 'False',
                        "--globalPositionsFile", '[]',
                        "--numberingPattern", scope_path,
                        "--startRow", '0',
                        "--startCol", '0',
                        "--extentWidth", str(grid_width),
                        "--extentHeight", str(grid_height),
                        "--timeSlices", z_list,
                        "--isTimeSlicesEnabled", 'True',
                        "--outputPath", str(output),
                        "--displayStitching", 'False',
                        "--outputFullImage", 'True',
                        "--outputMeta", 'True',
                        "--outputImgPyramid", 'False',
                        "--blendingMode", "OVERLAY",
                        "--blendingAlpha", "NaN",
                        "--outFilePrefix", outfile,
                        "--programType", "AUTO",
                        "--numCPUThreads", "8",
                        "--loadFFTWPlan", 'True',
                        "--saveFFTWPlan", 'True',
                        '--fftwPlanType', "MEASURE",
                        '--fftwLibraryName', "libfftw3",
                        '--fftwLibraryFilename', "libfftw3.dll",
                        '--planPath', "lib/fftw/fftPlans",
                        '--fftwLibraryPath', "lib/fftw",
                        '--stageRepeatability', '0',
                        '--horizontalOverlap', "NaN",
                        '--verticalOverlap', "NaN",
                        '--numFFTPeaks', '0',
                        '--overlapUncertainty', "NaN",
                        '--isUseDoublePrecision', 'False',
                        '--isUseBioFormats', 'False',
                        '--isSuppressModelWarningDialog', 'False',
                        '--isEnableCudaExceptions', 'False',
                        '--translationRefinementMethod', "SINGLE_HILL_CLIMB",
                        '--numTranslationRefinementStartPoints', '16',
                        '--headless', 'True',
                        '--logLevel', "MANDATORY",
                        '--debugLevel', "NONE"
                        ]
                else:
                    args_primary = [
                        "--gridWidth", str(grid_width),
                        "--gridHeight", str(grid_height),
                        "--startTile", '1',
                        "--imageDir", str(image_set),
                        "--filenamePattern", start_file,
                        "--filenamePatternType", order,
                        "--gridOrigin", "UL",
                        "--assembleFromMetadata", 'False',
                        "--assembleNoOverlap", 'False',
                        "--globalPositionsFile", '[]',
                        "--numberingPattern", scope_path,
                        "--startRow", '0',
                        "--startCol", '0',
                        "--extentWidth", str(grid_width),
                        "--extentHeight", str(grid_height),
                        "--timeSlices", z_list,
                        "--isTimeSlicesEnabled", 'True',
                        "--outputPath", str(output),
                        "--displayStitching", 'False',
                        "--outputFullImage", 'True',
                        "--outputMeta", 'True',
                        "--outputImgPyramid", 'False',
                        "--blendingMode", "OVERLAY",
                        "--blendingAlpha", "NaN",
                        "--outFilePrefix", outfile,
                        "--programType", "AUTO",
                        "--numCPUThreads", "8",
                        "--loadFFTWPlan", 'True',
                        "--saveFFTWPlan", 'True',
                        '--fftwPlanType', "MEASURE",
                        '--fftwLibraryName', "libfftw3",
                        '--fftwLibraryFilename', "libfftw3.dll",
                        '--planPath', "lib/fftw/fftPlans",
                        '--fftwLibraryPath', "lib/fftw",
                        '--stageRepeatability', '0',
                        '--horizontalOverlap', "NaN",
                        '--verticalOverlap', "NaN",
                        '--numFFTPeaks', '0',
                        '--overlapUncertainty', "NaN",
                        '--isUseDoublePrecision', 'False',
                        '--isUseBioFormats', 'False',
                        '--isSuppressModelWarningDialog', 'False',
                        '--isEnableCudaExceptions', 'False',
                        '--translationRefinementMethod', "SINGLE_HILL_CLIMB",
                        '--numTranslationRefinementStartPoints', '16',
                        '--headless', 'True',
                        '--logLevel', "MANDATORY",
                        '--debugLevel', "NONE"
                        ]
                final_args = java_args + args_primary
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
                        if " " in str(image_dir):
                            args_secondary = [
                                    "--gridWidth", str(grid_width),
                                    "--gridHeight", str(grid_height),
                                    "--startTile", '1',
                                    "--imageDir", "'"+str(other_dir/t)+"'",
                                    "--filenamePattern", channel_set,
                                    "--filenamePatternType", order,
                                    "--gridOrigin", "UL",
                                    "--assembleFromMetadata", 'True',
                                    "--assembleNoOverlap", 'False',
                                    "--globalPositionsFile", str(output/(outfile+ 'global-positions-{t}.txt')),
                                    "--numberingPattern", scope_path,
                                    "--startRow", '0',
                                    "--startCol", '0',
                                    "--extentWidth", str(grid_width),
                                    "--extentHeight", str(grid_height),
                                    "--timeSlices", z_list,
                                    "--isTimeSlicesEnabled", 'True',
                                    "--outputPath", str(output),
                                    "--displayStitching", 'False',
                                    "--outputFullImage", 'True',
                                    "--outputMeta", 'True',
                                    "--outputImgPyramid", 'False',
                                    "--blendingMode", "OVERLAY",
                                    "--blendingAlpha", "NaN",
                                    "--outFilePrefix", t+ '_'+prefix[channel],
                                    "--programType", "AUTO",
                                    "--numCPUThreads", "8",
                                    "--loadFFTWPlan", 'True',
                                    "--saveFFTWPlan", 'True',
                                    '--fftwPlanType', "MEASURE",
                                    '--fftwLibraryName', "libfftw3",
                                    '--fftwLibraryFilename', "libfftw3.dll",
                                    '--planPath', "lib/fftw/fftPlans",
                                    '--fftwLibraryPath', "lib/fftw",
                                    '--stageRepeatability', '0',
                                    '--horizontalOverlap', "NaN",
                                    '--verticalOverlap', "NaN",
                                    '--numFFTPeaks', '0',
                                    '--overlapUncertainty', "NaN",
                                    '--isUseDoublePrecision', 'False',
                                    '--isUseBioFormats', 'False',
                                    '--isSuppressModelWarningDialog', 'False',
                                    '--isEnableCudaExceptions', 'False',
                                    '--translationRefinementMethod', "SINGLE_HILL_CLIMB",
                                    '--numTranslationRefinementStartPoints', '16',
                                    '--headless', 'True',
                                    '--logLevel', "MANDATORY",
                                    '--debugLevel', "NONE"
                                    ]
                        else:
                            args_secondary = [
                                "--gridWidth", str(grid_width),
                                "--gridHeight", str(grid_height),
                                "--startTile", '1',
                                "--imageDir", str(image_dir/t),
                                "--filenamePattern", channel_set,
                                "--filenamePatternType", order,
                                "--gridOrigin", "UL",
                                "--assembleFromMetadata", 'True',
                                "--assembleNoOverlap", 'False',
                                "--globalPositionsFile", str(output/(outfile+ 'global-positions-{t}.txt')),
                                "--numberingPattern", scope_path,
                                "--startRow", '0',
                                "--startCol", '0',
                                "--extentWidth", str(grid_width),
                                "--extentHeight", str(grid_height),
                                "--timeSlices", z_list,
                                "--isTimeSlicesEnabled", 'True',
                                "--outputPath", str(output),
                                "--displayStitching", 'False',
                                "--outputFullImage", 'True',
                                "--outputMeta", 'True',
                                "--outputImgPyramid", 'False',
                                "--blendingMode", "OVERLAY",
                                "--blendingAlpha", "NaN",
                                "--outFilePrefix", t+ '_'+prefix[channel],
                                "--programType", "AUTO",
                                "--numCPUThreads", "8",
                                "--loadFFTWPlan", 'True',
                                "--saveFFTWPlan", 'True',
                                '--fftwPlanType', "MEASURE",            
                                '--fftwLibraryName', "libfftw3",
                                '--fftwLibraryFilename', "libfftw3.dll",
                                '--planPath', "lib/fftw/fftPlans",
                                '--fftwLibraryPath', "lib/fftw",
                                '--stageRepeatability', '0',
                                '--stageRepeatability', '0',
                                '--horizontalOverlap', "NaN",
                                '--verticalOverlap', "NaN",
                                '--numFFTPeaks', '0',
                                '--overlapUncertainty', "NaN",
                                '--isUseDoublePrecision', 'False',
                                '--isUseBioFormats', 'False',
                                '--isSuppressModelWarningDialog', 'False',
                                '--isEnableCudaExceptions', 'False',
                                '--translationRefinementMethod', "SINGLE_HILL_CLIMB",
                                '--numTranslationRefinementStartPoints', '16',
                                '--headless', 'True',
                                '--logLevel', "MANDATORY",
                                '--debugLevel', "NONE"
                                ]
                        final_args = java_args + args_secondary
                        #run NIST with new arguments
                        run_result = subprocess.run(final_args, **extra_args)
        os.chdir(old_dir)
        return(run_result.returncode)

"""
fiji_loc = Path('/Applications/Fiji.app')
java_loc = Path('/Applications/Fiji.app/java/macosx/adoptopenjdk-8.jdk/jre/Contents/Home/bin/java')
data_dir = Path('/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse_corr/XY01')
sec_dir = Path('/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01')
name_key = ["2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH1.tif", "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH3_threshold.tiff",
             "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH4.tif", "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_Overlay.tif"]
prefixes = ["CH1", "CH3", "CH4", "Overlay"]
main_chan = 1
output_dir = Path("/Users/ConradOakes/Desktop/Galloway_2021/py_test")

stitching(fiji_dir = fiji_loc, java_dir = java_loc, main_dir = data_dir, name_keys = name_key, prefix = prefixes, template = main_chan,
              output = output_dir)
"""
