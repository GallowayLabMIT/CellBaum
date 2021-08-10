import shutil
import os
from pathlib import Path

"""
Merges the specified folders of images in the given order

input_dir: Directory containing different dpi folders
output_dir: Directory to put compiled images in
dpi_list: dpis to merge, in chronological order
regexp: the regular expression matching each image name
"""
def merge_dpi(input_dir, output_dir, dpi_list, regexp):
    future_time_to_add = 0
    time_to_add = 0
    #for each dpi folder...
    for dpis in dpi_list:
        # saves path
        dpi_path = Path(input_dir/dpis)
        # calculates time offset
        time_to_add = time_to_add+future_time_to_add
        #for each well folder...
        for wells in sorted(next(os.walk(dpi_path))[1]):
            # saves paths
            well_path = dpi_path/wells
            output_well = output_dir/wells
            # creates new folder if DNE
            if not (output_well.is_dir()):
                output_well.mkdir(parents = True)
            # saves time that will be added to the next dpi_folder
            future_time_to_add = len(next(os.walk(well_path))[1])
            # for each time folder...
            for time_folder in sorted(next(os.walk(well_path))[1]):
                # saves path
                time_path = well_path/time_folder
                # calculates new time
                time = int(time_folder[1:])
                time = time + time_to_add
                # creates new time folder
                output_time = output_well/f'T{time:04}'
                if not (output_time.is_dir()):
                    output_time.mkdir(parents = True)
                # for each image...
                for image in sorted(next(os.walk(time_path))[2]):
                    # creates new name and copies it to new folder
                    mo = regexp.search(image)
                    new_name = f'{mo.group("prefix")}_T{time:04}{mo.group("suffix")}.tif'
                    shutil.copy(time_path/image, output_time/new_name)

'''
format_regexp = re.compile(r"""(?P<prefix>.*)(?P<time>_T\d{4})(?P<suffix>.*).tif""", re.VERBOSE)
image_dir = Path("/Users/ConradOakes/CellBaum/output/")
final_dir = Path("/Users/ConradOakes/CellBaum/output/renamed")
dpi_order = ["2dpi", "3dpi"]
'''