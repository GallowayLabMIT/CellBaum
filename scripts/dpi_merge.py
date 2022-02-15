import shutil
import os
from pathlib import Path
import re
from typing import List

"""
Merges the specified folders of images in the given order
Parameters
----------
input_dir: Path
    Directory containing different dpi folders
output_dir: Path
    Directory to put compiled images in
dpi_list: List of strings
    The dpis to merge, in chronological order
Return
------
None
"""
def merge_dpi(input_dir:Path, output_dir:Path, dpi_list:List[str])->None:
    future_time_to_add = 0
    time_to_add = 0
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    #for each dpi folder...
    for dpis in dpi_list:
        # saves path
        dpi_path = input_dir/dpis
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
                    new_name = re.sub("(?P<time>T\d{4})", f'T{time:04}', image)
                    shutil.copy(time_path/image, output_time/new_name)

'''
format_regex = re.compile(r"""(?P<prefix>.*)_(?P<time>T\d{4})_(?P<well>XY\d{2})_(?P<position>\d{5})_Z(?P<stack>.{3})_(?P<channel>.*)\.tif""", re.VERBOSE)
image_dir = Path("/Users/ConradOakes/CellBaum/output/")
final_dir = Path("/Users/ConradOakes/CellBaum/output/renamed")
dpi_order = ["2dpi", "3dpi"]
merge_dpi(image_dir, final_dir, dpi_order, format_regex)
'''
