from stitching_function import stitching
configfile: "cellbaum_config.yml"

import pathlib
import os
WELL = []
for check in pathlib.Path(config["data_dir"]).iterdir():
    if check.is_dir():
        w = os.path.basename(os.path.normpath(check))
        WELL.append(w)

rule all:
	input: 
		expand(config["output_dir"]+'/{well}cell_data', well = WELL)

rule find_corr:
	input:
		image_dir = config["data_dir"] + '/{well}'
	params:
		cp_app = config["cp_loc"],
		pipeline = config["pipe_loc"] + "/illum_func.cppipe"
	log:
		config["log_loc"] + "/{well}find_corr_log.txt"
	output:
		illum_func = config["data_dir"] + '/{well}' + "/{well}_illum_func.npy"
	shell:
		"{params.cp_app}/Contents/MacOS/cp -c -r -p {params.pipeline:q} --output-directory {input.image_dir:q} --image-directory {input.image_dir:q} &> {log}"

rule apply_corr:
	input:
		image_dir = config["data_dir"] + '/{well}',
		illum_func = config["data_dir"] + '/{well}' + "/{well}_illum_func.npy"
	params:
		cp_app = config["cp_loc"],
		pipeline = config["pipe_loc"] + "/apply_illum.cppipe",
	log:
		config["log_loc"] + "/{well}apply_corr_log.txt"
	output:
		image_dir = directory(config["data_dir"] + "_corr/{well}")
	shell:
		"{params.cp_app}/Contents/MacOS/cp -c -r -p {params.pipeline:q} --output-directory {output.image_dir:q} --image-directory {input.image_dir:q} &> {log}"

rule stitching:
	input:
		main_dir = config["data_dir"] + "_corr/{well}",
		sec_dir = config["data_dir"] + "/{well}"
	params:
		fiji_dir = config["fiji_loc"],
		name_keys = lambda wildcards : config["Name_keys"],
		prefix = config["Prefix"],
		template = config["Template"]
	log:
		config["log_loc"] + "/{well}stitching_log.txt"
	output:
		stitch_dir = directory(config["output_dir"] + "/{well}py_test")
	run:
		stitching(params.fiji_dir, input.main_dir, input.sec_dir, params.name_keys, params.prefix, params.template, output.stitch_dir, "{wildcards.well}", log[0])

rule find_objects:
	input:
		image_dir = config["output_dir"] + "/{well}py_test"
	params:
		cp_app = config["cp_loc"],
		pipeline = config["pipe_loc"] + "/nuclei_masking.cppipe",
	log:
		config["log_loc"] + "/{well}find_objects_log.txt"
	output:
		object_dir = directory(config["output_dir"] + '/{well}cell_data')
	shell:
		"{params.cp_app}/Contents/MacOS/cp -c -r -p {params.pipeline:q} --output-directory {output.object_dir:q} --image-directory {input.image_dir:q} &> {log}"
