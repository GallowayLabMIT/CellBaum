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
    # for each time point folder in the given directory.... (minus the first, which is .DS_Store)
    for image_set in sorted(os.listdir(dirs))[1:]:
        #create the path to the specific folder, for some reason double quotes are needed...
        image_dir = "'"+ dirs + '/'+image_set+"'"
        #create the regular expression for each image in that folder
        start_file = name_keys[template]
        start_file = start_file.replace('time', image_set)
        #name the output file
        outfile = image_set+'_'+prefix[template]
        #switch to the java directory
        os.chdir(fiji_dir)
        #create arguments
        args_primary = [
            "--gridWidth", '5',
            "--gridHeight", '5',
            "--startTile", '1',
            "--imageDir", image_dir,
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
            '--fftwLibraryName', "libfftw3",
            '--fftwLibraryFilename', "libfftw3.dll",
            '--planPath', "/Applications/Fiji.app/lib/fftw/fftPlans",
            '--fftwLibraryPath', "/Applications/Fiji.app/lib/fftw",
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
                channel_set = channel_set.replace('time', image_set)
                #create arguments assembling from the template channel's metadata
                args_secondary = [
                        "--gridWidth", '5',
                        "--gridHeight", '5',
                        "--startTile", '1',
                        "--imageDir", image_dir,
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
                        "--outFilePrefix", image_set+ '_'+prefix[channel],
                        "--programType", "AUTO",
                        "--numCPUThreads", "8",
                        "--loadFFTWPlan", 'True',
                        "--saveFFTWPlan", 'True',
                        '--fftwPlanType', "MEASURE",
                        '--fftwLibraryName', "libfftw3",
                        '--fftwLibraryFilename', "libfftw3.dll",
                        '--planPath', "/Applications/Fiji.app/lib/fftw/fftPlans",
                        '--fftwLibraryPath', "/Applications/Fiji.app/lib/fftw",
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
    sys.exit(run_result.returncode)
    os.chdir(old_dir)

java_loc = '/Applications/Fiji.app'
data_dir = '/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01'
name_key = ["2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH1.tif", "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH3_corrected.tiff",
             "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH4.tif", "2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_Overlay.tif"]
prefixes = ["CH1", "CH3", "CH4", "Overlay"]
main_chan = 1
output_dir = "/Users/ConradOakes/Desktop/Galloway_2021/py_test"

stitching(fiji_dir = java_loc, dirs = data_dir, name_keys = name_key, prefix = prefixes, template = main_chan,
              output = output_dir)
        