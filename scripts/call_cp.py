#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Christopher Johnstone
"""
import subprocess

def call_cp(cp_exe, pipeline_filename, output_dir, image_dir, logfile):
    """
    Uses CellProfiler to run a pipeline file.

    Arguments
    ---------
    cp_exe: A string or Path representing the location of the CellProfiler executable.
    pipeline_filename: A string or Path representing the .cppipe to run
    output_dir: The directory to put CellProfiler output in
    image_dir: The directory to load images from.
    logfile: The file to log output to.
    """
    run_args = [str(cp_exe),
                '-c', '-r', '-p',
                str(pipeline_filename),
                f'--output-directory={str(output_dir)}',
                f'--image-directory={str(image_dir)}']
    with open(logfile, 'w') as log:
        log.write('Starting CellProfiler with arguments {}\n'.format(run_args))
        run_result = subprocess.run(run_args, stdout=log, stderr=log)
        return run_result.returncode