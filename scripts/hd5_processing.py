import pandas as pd
import numpy as np
import h5py
import shutil
from pathlib import Path

def add_to_h5(dir, well, to_save):
    cp_loc = dir / (well+"cell_data") / "cell_locationsIdentifyPrimaryObjects.csv"
    cp_data = pd.read_csv(cp_loc)
    v_track = dir / 'btrack_results' / (well+'tracks.h5')
    cp_track = dir / 'btrack_results' / (well+'tracks_cp.h5')
    shutil.copy (v_track, cp_track)
    cp_track = h5py.File(cp_track, 'a')
    if to_save == 'all':
        for col in list(cp_data.columns):
            if '/cp_data/obj_type_1/' not in cp_track:
                cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(cp_data[col]))
            if (col not in list(cp_track['cp_data']['obj_type_1'])):
                cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(cp_data[col]))
    else:
        for col in list(cp_data.columns):
            if (col in to_save) and ('/cp_test/obj_type_1/' not in cp_track):
                cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(cp_data[col]))
            if (col in to_save) and (col not in list(cp_track['cp_data']['obj_type_1'])):
                cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(cp_data[col]))

"""
output = Path("/Users/ConradOakes/CellBaum/output")
w = 'XY01'
save = 'all'
add_to_h5(output, w, save)
"""

