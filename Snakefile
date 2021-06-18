#get dependencies
from scripts.env_validation import val_env
from scripts.stitching_function import stitching
from scripts.btracker import btracking
from scripts.hd5_processing import add_to_h5
configfile: "cellbaum_config.yml"
from pathlib import Path
import os
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
		expand(Path(config["output_dir"]) / "btrack_results"/"{well}tracks_cp.h5", well = WELL)

rule process_image:
	input: 
		image_dir = Path(config["data_dir"]) / '{well}'
	params:
		pipeline = Path(config["pipe_loc"]) / "img_processing.cppipe"
	log:
		Path(config["log_loc"]) / "{well}img_processing_log.txt"
	output:
		image_dir = directory(Path((config["data_dir"] + "_corr"+"/{well}")))
	shell:
		"{cp_app} -c -r -p {params.pipeline:q} --output-directory {output.image_dir:q} --image-directory {input.image_dir:q} &> {log}"
 
rule stitching:
	input:
		main_dir = Path(config["data_dir"] + "_corr" + "/{well}"),
		sec_dir = Path(config["data_dir"]) / "{well}"
	params:
		name_keys = lambda wildcards : config["Name_keys"],
		prefix = config["Prefix"],
		template = config["Template"]
	log:
		Path(config["log_loc"]) / "{well}stitching_log.txt"
	output:
		stitch_dir = directory(Path(config["output_dir"]) / "{well}py_test")
	run:
		stitching(fiji_app, java_app, input.main_dir, input.sec_dir, params.name_keys, params.prefix, params.template, output.stitch_dir, log[0])

rule cp_process:
	input:
		temp = Path(config["pipe_loc"])/"nuclei_masking.cppipe.template"
	output:
		final = Path(config["pipe_loc"])/"nuclei_masking.cppipe"
	run:
		with open(Path(config["pipe_loc"])/"nuclei_masking.cppipe.template") as infile, open(Path(config["pipe_loc"])/"nuclei_masking.cppipe", "w") as outfile:
			outfile.write(infile.read().replace("!MINSIZE!", config['minsize']).replace("!MAXSIZE!", config['maxsize']))

rule find_objects:
	input:
		image_dir = Path(config["output_dir"]) / "{well}py_test"
	params:
		pipeline = Path(config["pipe_loc"]) / "nuclei_masking.cppipe",
	log:
		Path(config["log_loc"]) / "{well}find_objects_log.txt"
	output:
		object_dir = directory(Path(config["output_dir"]) / '{well}cell_data'),
        	out_csv = Path(config["output_dir"]) / '{well}cell_data' / 'cell_locationsIdentifyPrimaryObjects.csv'
	shell:
		"{cp_app} -c -r -p {params.pipeline:q} --output-directory {output.object_dir:q} --image-directory {input.image_dir:q} &> {log}"

rule btrack:
	input:
		cp_csv = Path(config["output_dir"]) / '{well}cell_data' / 'cell_locationsIdentifyPrimaryObjects.csv'
	params:
		cell_configs = Path(config["cell_config"]),
		update = config["Update_method"],
		search = config["Max_search_radius"],
		vol = tuple(tuple(x) for x in config["Volume"]),
		step = config["Step_size"]
	log:
		Path(config["log_loc"]) / "{well}btrack_log.txt"
	output:
		final_data = Path(config["output_dir"]) / "btrack_results"/"{well}tracks.h5"
	run:
		btracking(input.cp_csv, params.cell_configs, output.final_data, 
			params.update, params.search, params.vol, params.step)


rule h5_add:
	input: 
		cp_csv = Path(config["output_dir"]),
		initial_data = Path(config["output_dir"]) / "btrack_results"/"{well}tracks.h5"
	params:
		w = "{well}",
		add_on = config["CP_Data_Keep"]
	output:
		final_data = Path(config["output_dir"]) / "btrack_results"/"{well}tracks_cp.h5"
	run:
		add_to_h5(input.cp_csv, params.w, params.add_on)
