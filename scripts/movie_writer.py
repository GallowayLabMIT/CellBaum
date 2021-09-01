import h5py
import matplotlib
import matplotlib.cm
import numpy as np
from numpy.core.numeric import zeros_like
from scipy import signal, ndimage
from PIL import ImageDraw, Image

import re
import itertools
from pathlib import Path
import random

from typing import Union

def cmap_to_ids(cmap_image: Image.Image, centers: np.ndarray) -> np.ndarray:
    """
    Converts a cryptomatte image into a flattened representation where
    instead of a 3D color image, we have a 2D image where entries are
    unique object numbers (e.g. not shared across colors)
    """
    pixel_data = np.array(cmap_image)
    _, flattened = np.unique(pixel_data.reshape(-1,3), axis=0, return_inverse=True)
    flattened = np.array(flattened.reshape(pixel_data.shape[:2]), dtype='uint16')
    markers = np.zeros_like(flattened, dtype=int)

    approx_centers = np.array(centers, dtype=int)
    markers[approx_centers[:,1], approx_centers[:,0]] = range(1, 1 + centers.shape[0])
    return ndimage.watershed_ift(flattened, markers)

def outline(boolean_mask: np.ndarray) -> np.ndarray:
    """
    Given a boolean mask representing a filled image, uses a convolution
    to outline the given object, returning a boolean array of this convolution.
    """
    return ndimage.laplace(boolean_mask)


def write_frames(output_dir: Union[str, Path],
                 track_data: Union[str, Path],
                 stitched_dir: Union[str, Path],
                 stitched_regex: str,
                 cryptomatte_dir: Union[str, Path],
                 cryptomatte_regex: str,
                 max_obj_size: int,
                 viz_type: str) -> None:
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
    max_obj_size:       The largest object that was recorded (used for speeding up drawing)
    viz_type:           A string, either 'outline' for simple outlining, 'children' for the child
                        graph, or another string to lookup from the HDF5 file.
    
    Returns
    -------
    None, but outputs files into output_dir.
    """
    base_color = [157, 5, 252]
    trail_length = 5

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
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
        print('Stitched images and cryptomattes registered successfully.\nPrecomputing...', end='', flush=True)

        # Create segment mapping
        segments = {k: [] for k in sorted(image_map.keys())[1:]}
        # Iterate over segment table, building hue mapping and segment mapping
        track_group = track_data['tracks']['obj_type_1']
        hue_mapping = np.zeros_like(track_data['objects']['obj_type_1']['coords'][:,0])
        lbepr = track_group['LBEPR'][:,:5]
        for track_idx in range(lbepr.shape[0]):
            # If we are our own root, then assign random color. Otherwise, offset from parent color
            if lbepr[track_idx,0] == lbepr[track_idx,4]:
                hue = random.randint(0,255)
            else:
                hue = (hue_mapping[lbepr[track_idx,3]] + random.randint(-15,15)) % 255
            
            tracks = track_group['tracks'][track_group['map'][track_idx,0]:track_group['map'][track_idx,1]]
            if len(tracks) != lbepr[track_idx,2] - lbepr[track_idx,1] + 1:
                continue
            # Compute segments
            segment_locs = np.zeros((tracks.shape[0],2))
            for i, obj_idx in enumerate(tracks):
                if obj_idx < 0:
                    segment_locs[i,:] = track_group['dummies'][-1 - obj_idx,1:3]
                else:
                    segment_locs[i,:] = track_data['objects']['obj_type_1']['coords'][obj_idx, 1:3]
                    hue_mapping[obj_idx] = hue
            for i, k in enumerate(range(lbepr[track_idx,1], lbepr[track_idx,2])):
                segments[k + 1].append([
                    segment_locs[i,0], segment_locs[i,1],
                    segment_locs[i+1,0], segment_locs[i+1,1]
                ])
        # If the viz type is something else, try to look it up now and convert to colors with viridis.
        if viz_type not in ['outline', 'children']:
            values = track_data['cp_data']['obj_type_1'][viz_type]
            min_val = np.min(values)
            max_val = np.max(values)
            viridis = matplotlib.cm.get_cmap('viridis', 255)
            rescaled_values = (values - min_val) / (max_val - min_val)
            viz_map = viridis(rescaled_values)

        print('done!', flush=True)
        # At this point, for every time point we have the path to the cryptomatte and the stitched image.
        twidth = int(np.ceil(np.log10(len(image_map))))
        for timepoint in sorted(image_map.keys()):
            print(f'Rendering frame {timepoint}:')
            files = image_map[timepoint]
            object_idx = np.where(track_data['objects']['obj_type_1']['coords'][:,0] == timepoint)[0]
            # Open the stitched and cryptomatte images
            with Image.open(files['stitch']) as stitched_image, Image.open(files['cmap']) as cmap_image:
                # Generate object id mask
                pixel_obj_ids = cmap_to_ids(cmap_image, track_data['objects']['obj_type_1']['coords'][object_idx,1:3])
                # Create overlay drawer
                drawer = ImageDraw.Draw(stitched_image, 'RGBA')
                # Draw all relevant tracks
                for trail_class in range(timepoint - trail_length, timepoint + 1):
                    if trail_class in segments:
                        for segment in segments[trail_class]:
                            drawer.line(segment, fill=(
                                *base_color,
                                int(255 * (trail_class - (timepoint - trail_length)) / trail_length)))
                print('\tDone drawing trails\n\tDrawing objects.', end='', flush=True)
                for idx, object in enumerate(object_idx):
                    object_location = track_data['objects']['obj_type_1']['coords'][object,1:3]
                    obj_id = pixel_obj_ids[int(object_location[1]), int(object_location[0])]
                    # Clip to region within +- max object size
                    upper_left = (int(max(0, object_location[1] - max_obj_size)),
                                  int(max(0, object_location[0] - max_obj_size)))
                    rev_upper_left = (upper_left[1], upper_left[0])
                    lower_right = (int(min(pixel_obj_ids.shape[0], object_location[1] + max_obj_size)),
                                   int(min(pixel_obj_ids.shape[1], object_location[0] + max_obj_size)))
                    cropped = pixel_obj_ids[upper_left[0]:lower_right[0], upper_left[1]:lower_right[1]]
                    if viz_type == 'outline':
                        pass
                    elif viz_type == 'children':
                        obj_color = matplotlib.colors.hsv_to_rgb(
                            np.array([hue_mapping[object] / 255, 0.6, 0.9]))
                        drawer.bitmap(rev_upper_left, Image.fromarray(cropped == obj_id),
                            tuple(int(255 * x) for x in obj_color))
                    else:
                        drawer.bitmap(rev_upper_left, Image.fromarray(cropped == obj_id),
                            tuple(int(255 * x) for x in viz_map[object,:]))
                    drawer.bitmap(
                        rev_upper_left,
                        Image.fromarray(outline(cropped == obj_id)),
                        tuple(base_color))
                    if idx % 10 == 0:
                        print('.', end='', flush=True)
                print('',flush=True)
                stitched_image.save(output_dir / f"T{timepoint:0{twidth}}.tiff")

base_output = "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/movie_output"

b_args = [
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/btrack_results/XY03/tracks_cp.h5",
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/stitched/XY03",
    r"T(\d{4})_CH3stitched-1.tif",
    "C:/Users/ChemeGrad2019/Massachusetts Institute of Technology/GallowayLab - Documents/projects/Consortia/KTR-Timelapse/cell_data/XY03",
    r"T(\d{4})_CH3stitched-1_Objects.tiff",
    50
]

write_frames(base_output + '/b/outline', *b_args, 'outline')
write_frames(base_output + '/b/children', *b_args, 'children')
write_frames(base_output + '/b/TagBFP', *b_args, 'Intensity_MeanIntensity_Blue')
write_frames(base_output + '/b/red', *b_args, 'Intensity_MeanIntensity_Red')

c_args = [
    "C:/Users/ChemeGrad2019/source/repos/CellBaum/test_output_conrad/btrack_results/XY01/tracks_cp.h5",
    "C:/Users/ChemeGrad2019/source/repos/CellBaum/test_output_conrad/stitched/XY01",
    r"T(\d{4})_Overlaystitched-1.tif",
    "C:/Users/ChemeGrad2019/source/repos/CellBaum/test_output_conrad/cell_data/XY01",
    r"T(\d{4})_CH3stitched-1_Objects.tiff",
    50
]

write_frames(base_output + '/c/outline',  *c_args, 'outline')
write_frames(base_output + '/c/children', *c_args, 'children')
