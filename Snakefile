#get dependencies
from scripts.env_validation import val_env
from scripts.stitching_function import stitching
from scripts.btracker import btracking
configfile: "cellbaum_config.yml"
import pathlib
import os
#find required apps
cp_app, fiji_app, java_app = val_env(config["base_dir"])
#generate list of wells
WELL = []
for check in pathlib.Path(config["data_dir"]).iterdir():
    if check.is_dir():
        w = os.path.basename(os.path.normpath(check))
        WELL.append(w)

rule all:
	input: 
		expand(config["output_dir"] + "/btrack_results/{well}tracks.h5", well = WELL)

rule process_image:
	input: 
		image_dir = config["data_dir"] + '/{well}'
	params:
		pipeline = config["pipe_loc"] + "/img_processing.cppipe"
	log:
		config["log_loc"] + "/{well}img_processing_log.txt"
	output:
		image_dir = directory(config["data_dir"] + "_corr/{well}")
	shell:
		"{cp_app} -c -r -p {params.pipeline:q} --output-directory {output.image_dir:q} --image-directory {input.image_dir:q} &> {log}"
 
rule stitching:
	input:
		main_dir = config["data_dir"] + "_corr/{well}",
		sec_dir = config["data_dir"] + "/{well}"
	params:
		name_keys = lambda wildcards : config["Name_keys"],
		prefix = config["Prefix"],
		template = config["Template"]
	log:
		config["log_loc"] + "/{well}stitching_log.txt"
	output:
		stitch_dir = directory(config["output_dir"] + "/{well}py_test")
	run:
		stitching(fiji_app, java_app, input.main_dir, input.sec_dir, params.name_keys, params.prefix, params.template, output.stitch_dir, log[0])

rule find_objects:
	input:
		image_dir = config["output_dir"] + "/{well}py_test"
	params:
		pipeline = config["pipe_loc"] + "/nuclei_masking.cppipe",
	log:
		config["log_loc"] + "/{well}find_objects_log.txt"
	output:
		object_dir = directory(config["output_dir"] + '/{well}cell_data')
	shell:
		"{cp_app} -c -r -p {params.pipeline:q} --output-directory {output.object_dir:q} --image-directory {input.image_dir:q} &> {log}"

rule btrack:
	input:
		main_dir = config["output_dir"] + '/{well}cell_data',
		output_dir = config["output_dir"] + "/btrack_results"
	params:
		cell_configs = config["cell_config"],
		w = "{well}",
		update = config["Update_method"],
		search = config["Max_search_radius"],
		vol = tuple(tuple(x) for x in config["Volume"]),
		step = config["Step_size"]
	log:
		config["log_loc"] + "/{well}btrack_log.txt"
	output:
		final_data = (config["output_dir"] + "/btrack_results/{well}tracks.h5")
	run:
		btracking(input.main_dir, params.cell_configs, input.output_dir, params.w, 
			params.update, params.search, params.vol, params.step)
