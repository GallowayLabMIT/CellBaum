#get dependencies
from scripts.env_validation import val_env
from scripts.stitching_function import stitching
from scripts.stitching_function import get_namekeys
from scripts.btracker import btracking
from scripts.btracker import get_image_dims
from scripts.call_cp import call_cp
from scripts.hd5_processing import add_to_h5
from scripts.dpi_merge import merge_dpi
from scripts.focus_point import find_focus
configfile: "cellbaum_config.yml"
from pathlib import Path
import os
import shutil
import re
import contextlib
#find required apps
print(config)
cp_app, fiji_app, java_app = val_env(Path(config["cp_dir"]), Path(config["fiji_dir"]))
# generate name keys for stitching
name_keys = get_namekeys(config["example_img_name"], config["Prefix"], config["image_regex"], 
        focused = config["focus_finding_needed"])
print(name_keys)
#generate list of wells
WELL = []
if 'folders_to_merge' in config:
    well_path = Path(config["data_dir"])/config['folders_to_merge'][0]
else:
    well_path = Path(config["data_dir"])

for check in well_path.iterdir():
    if check.is_dir():
        w = os.path.basename(os.path.normpath(check))
        WELL.append(w)
        
last_dir = Path(config["data_dir"])

rule all:
    input: 
        expand(Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks_cp.h5", well = WELL)

if config["folder_merging_needed"]:
    rule merge_dpi:
        input:
            image_dir = last_dir
        params:
            merging_wells = config["folders_to_merge"]
        output:
            image_dir = directory(Path(config["output_dir"])/"merged"),
            individual_folders = directory(expand(Path(config["output_dir"])/"merged"/"{well}", well = WELL))
        run:
            merge_dpi(input.image_dir,
                    output.image_dir,
                    params.merging_wells)
    last_dir = Path(config["output_dir"])/"merged"

if config["focus_finding_needed"]:
    rule find_focus:
        input:
            image_dir = last_dir/"{well}"
        params:
            regex = re.compile(config["image_regex"], re.VERBOSE),
            channels = config["focus_channels"]
        output:
            image_dir = directory(Path(config["output_dir"]) / "focused"/ "{well}")
        run:
            find_focus(input.image_dir, 
                        output.image_dir,
                        params.regex, 
                        params.channels)
    last_dir = Path(config["output_dir"]) / "focused"

if config["pre_stitch_correction_needed"]:
    rule process_image:
        input: 
            image_dir = last_dir/"{well}"
        params:
            pipeline = Path(config["pipe_dir"]) / "img_processing.cppipe"
        log:
            Path(config["log_dir"]) / "{well}img_processing_log.txt"
        output:
            image_dir = directory(Path(config["output_dir"]) /"corrected"/"{well}")
        run:
            shutil.copytree(input.image_dir, output.image_dir, dirs_exist_ok=True)
            call_cp(cp_app, params.pipeline, output.image_dir, input.image_dir, log[0])
    last_dir = Path(config["output_dir"])/"corrected"

rule stitching:
    input:
        main_dir = last_dir/"{well}"
    params:
        prefix = config["Prefix"],
        template = config["Template"],
        grid_width = config["stitching"]["grid_width"],
        grid_height = config["stitching"]["grid_height"],
        z_extent = None if 'z_min' not in config['stitching'] else (config['stitching']['z_min'], config['stitching']['z_max'])
    log:
        Path(config["log_dir"]) / "{well}stitching_log.txt"
    output:
        stitch_dir = directory(Path(config["output_dir"]) / "stitched"/"{well}")
    run:
        stitching(fiji_app, java_app, input.main_dir, name_keys,
                   params.prefix, params.template, params.grid_width, params.grid_height, 
                  output.stitch_dir, params.z_extent, log[0])

rule cp_process:
    input:
        temp = Path(config["pipe_dir"])/"nuclei_masking.cppipe.template"
    output:
        final = Path(config["pipe_dir"])/"nuclei_masking.cppipe"
    run:
        with open(Path(config["pipe_dir"])/"nuclei_masking.cppipe.template") as infile, open(Path(config["pipe_loc"])/"nuclei_masking.cppipe", "w") as outfile:
            outfile.write(infile.read().replace("!MINSIZE!", str(config['minsize'])).replace("!MAXSIZE!", str(config['maxsize'])))

rule find_objects:
    input:
        image_dir = Path(config["output_dir"]) / "stitched" / "{well}"
    params:
        pipeline = Path(config["pipe_dir"]) / "nuclei_masking.cppipe"
    log:
        Path(config["log_dir"]) / "{well}find_objects_log.txt"
    output:
        object_dir = directory(Path(config["output_dir"]) / 'cell_data'/"{well}"),
        out_csv = Path(config["output_dir"]) / 'cell_data'/'{well}' / 'cell_locationsIdentifyPrimaryObjects.csv'
    run:
        call_cp(cp_app, params.pipeline, output.object_dir, input.image_dir, log[0])

rule btrack:
    input:
        cp_csv = Path(config["output_dir"]) / 'cell_data' /"{well}"/ 'cell_locationsIdentifyPrimaryObjects.csv'
    params:
        cell_configs = Path(config["cell_config"]),
        update = config["Update_method"],
        search = config["Max_search_radius"],
        vol = tuple(tuple(config["Volume"][key]) for key in ["x", "y", "z"]),
        step = config["Step_size"]
    log:
        Path(config["log_dir"]) / "{well}btrack_log.txt"
    output:
        final_data = Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks.h5"
    run:
        btracking(input.cp_csv, params.cell_configs, output.final_data, 
            update=params.update, search=params.search, vol=params.vol, step=params.step, log_file = log[0])


rule h5_add:
    input: 
        cp_csv = Path(config["output_dir"])/"cell_data"/"{well}"/"cell_locationsIdentifyPrimaryObjects.csv",
        initial_data = Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks.h5"
    params:
        add_on = config["CP_Data_Keep"]
    output:
        final_data = Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks_cp.h5"
    run:
        add_to_h5(input.cp_csv, input.initial_data, params.add_on)
