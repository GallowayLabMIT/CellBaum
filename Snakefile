from stitching_function import stitching

rule find_corr:
	input:
		cp_app = "/Applications/CellProfiler.app/",
		pipeline = "/Users/ConradOakes/CellBaum/illum_func.cppipe",
		image_dir = "/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_short"
	output:
		illum_func = "/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_short/01_illum_func.npy"
	shell:
		"{input.cp_app:q}/Contents/MacOS/cp -c -r -p {input.pipeline:q} --output-directory {input.image_dir:q} --image-directory {input.image_dir:q}"

rule apply_corr:
	input:
		cp_app = "/Applications/CellProfiler.app",
		pipeline = "/Users/ConradOakes/CellBaum/apply_illum.cppipe",
		image_dir = "/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_short",
		illum_func = "/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_short/01_illum_func.npy"
	output:
		image_dir = directory("/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_corr")
	shell:
		"{input.cp_app:q}/Contents/MacOS/cp -c -r -p {input.pipeline:q} --output-directory {output.image_dir:q} --image-directory {input.image_dir:q}"

Name_keys = ['2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH1.tif', '2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH3_corrected.tiff', 
			'2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_CH4.tif', '2021.01.18_10X_time_XY01_000{pp}_Z{ttt}_Overlay.tif']
Prefix = ["CH1", "CH3", "CH4", "Overlay"]

rule stitching:
	input:
		fiji_dir = '/Applications/Fiji.app',
		main_dir = '/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_corr',
		sec_dir = '/Users/ConradOakes/Massachusetts Institute of Technology/GallowayLab - 2021.01.17.NT_FT_2dpi_timelapse/3dpi_timelapse/XY01_short',
		name_keys = Name_keys,
		prefix = Prefix,
		template = '1'
	output:
		stitch_dir = directory("/Users/ConradOakes/Desktop/Galloway_2021/py_test1")
	run:
		stitching(input.fiji_dir, input.main_dir, input.sec_dir, input.name_keys, input.prefix, input.template, output.stitch_dir)

rule find_objects:
	input:
		cp_app = "/Applications/CellProfiler.app/",
		pipeline = "/Users/ConradOakes/CellBaum/nuclei_masking.cppipe",
		image_dir = "/Users/ConradOakes/Desktop/Galloway_2021/py_test1"
	output:
		object_dir = directory('/Users/ConradOakes/Desktop/Galloway_2021/cell_data')
	shell:
		"{input.cp_app:q}/Contents/MacOS/cp -c -r -p {input.pipeline:q} --output-directory {output.image_dir:q} --image-directory {input.image_dir:q}"
