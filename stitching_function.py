#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 23:48:30 2021

@author: ConradOakes
"""
import subprocess
import sys
import os
import pathlib

"""
Uses NIST to stitch together sets of images. Requires the Fiji application to 
be installed and for it to have added the NIST plugin. 

fiji_dir: the path to the Fiji app
dirs: path to the folders of different time points
name_keys: a list of the regular expressions for the file names of each channel 
    (requires a position {p} and z {t} argument)
prefix: the names of each channel (for final output); should in the same order 
    as name_keys
template: the position in name_keys/prefix of the channel that is used as a 
    stitching template
output: the output directory
order: order of the positions in the {p} of name_keys (default = SEQUENTIAL)
scope_path: the microscopes path (defalut = HORIZONTALCONTINUOUS)
java_run: path to Fiji's built in Java program
"""
def stitching(fiji_dir, dirs, name_keys, prefix, template,
              output, order = "SEQUENTIAL", 
              scope_path = "HORIZONTALCONTINUOUS", z_list = "1-3"):
    fiji_paths = pathlib.Path(fiji_dir)
    fiji_ops = fiji_paths.glob('java/**/bin/java')
    for path in fiji_ops:
        if path.stem == 'java':
            java_run = path
            break
    else:
        raise RuntimeError("Explosion; no Java found")
    old_dir = os.getcwd()
    # for each time point folder in the given directory....
    dir_path = pathlib.Path(dirs)
    for image_set in dir_path.iterdir():
        if image_set.is_dir():
            #create the regular expression for each image in that folder
            t = os.path.basename(os.path.normpath(image_set))
            start_file = name_keys[template]
            start_file = start_file.replace('time', t)
            #name the output file
            outfile = t+'_'+prefix[template]
            #switch to the java directory
            os.chdir(fiji_dir)
            #create arguments
            args_primary = [
                "--gridWidth", '5',
                "--gridHeight", '5',
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
                "--extentWidth", '5',
                "--extentHeight", '5',
                "--timeSlices", z_list,
                "--isTimeSlicesEnabled", 'True',
                "--outputPath", output,
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
                '--fftwLibraryName', "/libfftw3",
                '--fftwLibraryFilename', "/libfftw3.dll",
                '--planPath', "/lib/fftw/fftPlans",
                '--fftwLibraryPath', "/lib/fftw",
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
            final_args = [java_run, '-cp', 
                                "plugins/MIST_.jar:jars/*", 'gov.nist.isg.mist.MISTMain']+ args_primary
            #run NIST with arguments
            run_result = subprocess.run(final_args)
            #for each channel other than the template...
            for channel in range(len(prefix)):
                if (channel) != template:
                    #set the name
                    channel_set =  name_keys[channel]
                    channel_set = channel_set.replace('time', t)
                    #create arguments assembling from the template channel's metadata
                    args_secondary = [
                            "--gridWidth", '5',
                            "--gridHeight", '5',
                            "--startTile", '1',
                            "--imageDir", "'"+str(image_set)+"'",
                            "--filenamePattern", channel_set,
                            "--filenamePatternType", order,
                            "--gridOrigin", "UL",
                            "--assembleFromMetadata", 'True',
                            "--assembleNoOverlap", 'False',
                            "--globalPositionsFile", output+'/'+outfile+ 'global-positions-{t}.txt',
                            "--numberingPattern", scope_path,
                            "--startRow", '0',
                            "--startCol", '0',
                            "--extentWidth", '5',
                            "--extentHeight", '5',
                            "--timeSlices", z_list,
                            "--isTimeSlicesEnabled", 'True',
                            "--outputPath", output,
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
                    final_args = [java_run, '-cp', 
                                "plugins/MIST_.jar:jars/*", 'gov.nist.isg.mist.MISTMain']+ args_secondary
                    #run NIST with new arguments
                    run_result = subprocess.run(final_args)
    os.chdir(old_dir)
    return(run_result.returncode)

java_loc = '/Applications/Fiji.app'
data_dir = '/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_short'
name_key = ["2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH1.tif", "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH3_corrected.tiff",
             "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH4.tif", "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_Overlay.tif"]
prefixes = ["CH1", "CH3", "CH4", "Overlay"]
main_chan = 1
output_dir = "/Users/ConradOakes/Desktop/Galloway_2021/py_test1"

stitching(fiji_dir = java_loc, dirs = data_dir, name_keys = name_key, prefix = prefixes, template = main_chan,
              output = output_dir)
        