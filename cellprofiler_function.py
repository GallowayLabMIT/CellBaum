#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 09:22:37 2021

@author: ConradOakes
"""

import subprocess
import sys
import os

"""
Runs a specified cellprofiler pipeline with the given image directory and output folder, 
creating subfolders mirroring the input directory.

cp_dir: the path to the CellProfiler app
pipe_dir: the path to the pipeline
output_dir: the output directory
image_dirs: path to the folders of different time points
"""
def run_cppipe(cp_dir, pipe_dir, output_dir, image_dirs, subfolders = True):
    old_dir = os.getcwd()   
    if subfolders == True :
        # for each time point folder in the given directory.... (minus the first, which is .DS_Store)
        for image_set in sorted(os.listdir(image_dirs))[1:]:
            #create the path to the specific folder
            images = image_dirs + '/'+image_set
            #go to the cellprofiler app
            os.chdir(cp_dir)
            #run the cppipe with a specified input and output folder
            args = ['Contents/MacOS/cp', '-c', '-r',
                '-p', pipe_dir,
                '--output-directory', output_dir+ '/'+image_set,
                '--image-directory', images
                ]
            run_result = subprocess.run(args)
            os.chdir(old_dir)
        sys.exit(run_result.returncode)
    else:
        #go to the cellprofiler app
        os.chdir(cp_dir)
        #run the cppipe with a specified input and output folder
        args = ['Contents/MacOS/cp', '-c', '-r',
                '-p', pipe_dir,
                '--output-directory', output_dir,
                '--image-directory', image_dirs
                ]
        run_result = subprocess.run(args)
        os.chdir(old_dir)
        sys.exit(run_result.returncode)

"""
cp= '/Applications/CellProfiler.app/'
cppipe_dir = '/Users/ConradOakes/Desktop/Galloway_2021/illum_corr.cppipe'
# output = '/Users/ConradOakes/Desktop/Galloway_2021/corr_test'
image = "/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01/"

run_cppipe(cp_dir = cp, pipe_dir = cppipe_dir, 
    output_dir = image, image_dirs = image)
"""
cp= '/Applications/CellProfiler.app/'
cppipe_dir = '/Users/ConradOakes/Desktop/Galloway_2021/nuclei_masking.cppipe'
image = '/Users/ConradOakes/Desktop/Galloway_2021/py_test'
output = '/Users/ConradOakes/Desktop/Galloway_2021/cell_data'

run_cppipe(cp_dir = cp, pipe_dir = cppipe_dir, 
    output_dir = output, image_dirs = image, subfolders = False)