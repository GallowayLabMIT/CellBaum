#get dependencies
from scripts.env_validation import val_env
from scripts.stitching_function import stitching
from scripts.btracker import btracking
from scripts.call_cp import call_cp
from scripts.hd5_processing import add_to_h5
configfile: "cellbaum_config.yml"
from pathlib import Path
import os
import shutil
#find required apps
cp_app, fiji_app, java_app = val_env(Path(config["cp_dir"]), Path(config["fiji_dir"]))
#generate list of wells
WELL = []
for check in Path(config["data_dir"]).iterdir():
    if check.is_dir():
        w = os.path.basename(os.path.normpath(check))
        WELL.append(w)

rule all:
    input: 
        expand(Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks_cp.h5", well = WELL)

rule process_image:
    input: 
        image_dir = Path(config["data_dir"]) / '{well}'
    params:
        pipeline = Path(config["pipe_dir"]) / "img_processing.cppipe"
    log:
        Path(config["log_dir"]) / "{well}img_processing_log.txt"
    output:
        image_dir = directory(Path(config["output_dir"]) /"corrected"/"{well}")
    run:
        shutil.copytree(input.image_dir, output.image_dir, dirs_exist_ok=True)
        call_cp(cp_app, params.pipeline, output.image_dir, input.image_dir, log[0])
 
if config["pre_stitch_correction_needed"]:
    stitching_dir = Path(config["output_dir"])/"corrected"/"{well}"
else:
    stitching_dir = Path(config["data_dir"])/"{well}"

rule stitching:
    input:
        main_dir = stitching_dir
    params:
        name_keys = lambda wildcards : config["Name_keys"],
        prefix = config["Prefix"],
        template = config["Template"],
        grid_width = config["stitching"]["grid_width"],
        grid_height = config["stitching"]["grid_height"],
        min_z = config["stitching"]["z_min"],
        max_z = config["stitching"]["z_max"]
    log:
        Path(config["log_dir"]) / "{well}stitching_log.txt"
    output:
        stitch_dir = directory(Path(config["output_dir"]) / "stitched"/"{well}")
    run:
        stitching(fiji_app, java_app, input.main_dir, params.name_keys,
                   params.prefix, params.template, params.grid_width, params.grid_height, 
                  output.stitch_dir, params.min_z, params.max_z, log[0])

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
            params.update, params.search, params.vol, params.step)


rule h5_add:
    input: 
        cp_csv = Path(config["output_dir"])/"cell_data"/"{well}"/"cell_locationsIdentifyPrimaryObjects.csv",
        initial_data = Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks.h5"
    params:
        w = "{well}",
        add_on = config["CP_Data_Keep"]
    output:
        final_data = Path(config["output_dir"]) / "btrack_results"/"{well}"/"tracks_cp.h5"
    run:
        add_to_h5(input.cp_csv, input.initial_data, params.w, params.add_on)
