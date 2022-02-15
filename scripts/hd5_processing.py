from ctypes import Union
import pandas as pd
import numpy as np
import h5py
import shutil
from pathlib import Path
import os

"""
Adds cell profiler data to an h5 file
Parameters
----------
cp_loc: Path
    The directory with the cell profiler csv
initial_h5: Path
    The path to the h5 file
to_save: List
    The list of cell profiler columns to save (or 'all' to save all cell profiler data)
z: int
    The z level used (default = 1)
Returns
-------
None
"""
def add_to_h5(cp_loc:Path, initial_h5:Path, to_save, z:int = 1)->None:
    # :Union[list(str), str]
    # opens cp csv
    cp_data = pd.read_csv(Path(cp_loc))
    # gets h5 file and creates copy to create a new h5 file
    v_track = Path(initial_h5)
    cp_track = Path(os.path.dirname(initial_h5))/'tracks_cp.h5'
    shutil.copy(v_track, cp_track)
    with h5py.File(cp_track, 'a') as cp_track:
        # filters cp_data by z level
        cp_data = cp_data.loc[cp_data['Metadata_zstep'] == z]

        # gets object data for each of t,x,y,z from the h5 file
        t_array = cp_track['objects']['obj_type_1']['coords'][:,0]
        x_array = cp_track['objects']['obj_type_1']['coords'][:,1]
        y_array = cp_track['objects']['obj_type_1']['coords'][:,2]
        z_array = cp_track['objects']['obj_type_1']['coords'][:,3]

        # gets cp data for t,x,y,z
        cp_t = cp_data['Metadata_time']
        cp_x = cp_data['Location_Center_X']
        cp_y = cp_data['Location_Center_Y']
        cp_z = cp_data['Metadata_zstep']

        index_order = []

        # for every object in the h5 file
        for n in range(len(cp_track['objects']['obj_type_1']['coords'])):
            if n%10000 == 0:
                print("At point " + str(n))
            # find all indices with the same value of t,x,y,or z
            index_t = np.isclose(t_array[n], cp_t).nonzero()
            index_x = np.isclose(x_array[n], cp_x).nonzero()
            index_y = np.isclose(y_array[n], cp_y).nonzero()
            index_z = np.isclose(z_array[n], cp_z).nonzero()
            # gets the index that appears in all 4
            index_final = set(index_t[0].tolist()) & set(index_x[0].tolist()) & set(index_y[0].tolist()) & set(index_z[0].tolist())
            if len(index_final) == 1:
                index_order.append(list(cp_data.iloc[int(list(index_final)[0])]))
            else:
                index_order.append([np.nan]*len(cp_data.columns))
        # creates dataframe of cell profiler data with all the cells sorted in the same order as in the h5
        ordered_cp = pd.DataFrame(index_order, columns = cp_data.columns)

        str_dtype = h5py.string_dtype(encoding='utf-8') 

        # saves all columns of cp_data to the new h5 file
        if to_save == 'all':
            for col in list(ordered_cp.columns):
                if (ordered_cp[col].dtype != 'O'):
                    if '/cp_data/obj_type_1/' not in cp_track:
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]))
                    if (col not in list(cp_track['cp_data']['obj_type_1'])):
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]))
                else:
                    if '/cp_data/obj_type_1/' not in cp_track:
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]), dtype = str_dtype)
                    if (col not in list(cp_track['cp_data']['obj_type_1'])):
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]), dtype = str_dtype)
        else:
            for col in list(ordered_cp.columns):
                if (ordered_cp[col].dtype != 'O'):
                    if (col in to_save) and ('/cp_test/obj_type_1/' not in cp_track):
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]))
                    if (col in to_save) and (col not in list(cp_track['cp_data']['obj_type_1'])):
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]))
                else:
                    if '/cp_data/obj_type_1/' not in cp_track:
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]), dtype = str_dtype)
                    if (col not in list(cp_track['cp_data']['obj_type_1'])):
                        cp_track.create_dataset('/cp_data/obj_type_1/' + col, data = np.array(ordered_cp[col]), dtype = str_dtype)


"""
output = Path("/Users/ConradOakes/CellBaum/output/cell_data/XY01/cell_locationsIdentifyPrimaryObjects.csv")
h5 = Path("/Users/ConradOakes/CellBaum/output/btrack_results/XY01/old_tracks.h5")
save = 'all'
add_to_h5(output, h5, save)
"""