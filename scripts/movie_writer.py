import h5py
import numpy as np
from PIL import ImageDraw, Image

import re
import itertools
from pathlib import Path

from typing import Union

def object_bitmask(cmap_pixels, image_size, x:float, y:float) -> np.ndarray:
    """
    Uses a Watershed-like algorithm to return a bitmask for the given object,
    using a pixel value x/y and the cryptomatte image.
    """
    result = np.array(image_size, dtype=bool)
    start_x, start_y = (int(x), int(y))
    color = cmap_pixels[start_x, start_y]
    
    queue = [(start_x, start_y)]

    while len(queue) > 0:
        pixel = queue.pop(0)
        result[pixel[0], pixel[1]] = True


def write_frames(output_dir: Union[str, Path],
                 track_data: Union[str, Path],
                 stitched_dir: Union[str, Path],
                 stitched_regex: str,
                 cryptomatte_dir: Union[str, Path],
                 cryptomatte_regex: str) -> None:
    """
    Writes out TIFF images with various overlays.

    Arguments
    ---------
    output_dir:         The folder in which overlaid TIFF images should be placed.
    track_data:         A path to the HDF5 file that stores btracked track information.
    stitched_dir:       The path to the folder that contains the full stitched images.
    stitched_regex:     A regular expression with one capture-group for timepoints.
    cryptomatte_dir:    The path to the folder that contains the cryptomatte images.
                        This path is typically the final CellProfiler output folder.
    cryptomatte_regex:  A regular expression with one capture-group for timepoints. This regex
                        is matched against the stitched regex.
    
    Returns
    -------
    None, but outputs files into output_dir.
    """

    with h5py.File(track_data, 'r') as track_data:
        image_map = {}
        for child in Path(stitched_dir).iterdir():
            match = re.fullmatch(stitched_regex, child.name)
            if match is None:
                continue
            image_map[int(match.group(1))] = {'stitch': child, 'cmap': None}
        for child in Path(cryptomatte_dir).iterdir():
            match = re.fullmatch(cryptomatte_regex, child.name)
            if match is None:
                continue
            if int(match.group(1)) not in image_map:
                raise RuntimeError(f"Cryptomatte {child.name} does not have a corresponding stitched image!")
            image_map[int(match.group(1))]['cmap'] = child
        # Check that all stitched images loaded have corresponding cryptomattes
        for v in image_map.values():
            if v['cmap'] is None:
                raise RuntimeError(f"Stitched image {v['stitch'].name} does not have a corresponding cryptomatte!")

        # At this point, for every time point we have the path to the cryptomatte and the stitched image.
        for timepoint in sorted(image_map.keys()):
            files = image_map[timepoint]
            object_idx = np.where(track_data['objects']['obj_type_1']['coords'][:,0] == timepoint)
            # Open the stitched and cryptomatte images
            with Image.open(files['stitch']) as stitched_image, Image.open(files['cmap']) as cmap_image:
                drawer = ImageDraw.Draw(stitched_image)
                cmap_pixels = cmap_image.load()


                print(stitched_image.size)
                for object in object_idx:
                    pass


                pass


write_frames(
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/movie_output",
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/btrack_results/XY03/tracks_cp.h5",
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/stitched/XY03",
    r"T(\d{4})_CH3stitched-1.tif",
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/cell_data/XY03",
    r"T(\d{4})_CH3stitched-1_Objects.tiff"
)