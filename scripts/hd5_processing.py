from numpy.core.fromnumeric import nonzero
import pandas as pd
import numpy as np
import h5py
import shutil
from pathlib import Path

from pandas._libs.missing import NA

def add_to_h5(dir, well, to_save):
    cp_loc = Path(dir) / (well+"cell_data") / "cell_locationsIdentifyPrimaryObjects.csv"
    cp_data = pd.read_csv(cp_loc)
    v_track = Path(dir) / 'btrack_results' / (well+'tracks.h5')
    cp_track = Path(dir) / 'btrack_results' / (well+'tracks_cp.h5')
    shutil.copy(v_track, cp_track)
    with h5py.File(cp_track, 'a') as cp_track:
        """
        cp_cols = cp_data.columns
        ref_track = pd.DataFrame(cp_track['objects']['obj_type_1']['coords'], columns = ['Metadata_time', 'Location_Center_X', 
            'Location_Center_Y', 'Metadata_zstep', 'other'])

        merge_track = pd.merge(ref_track, cp_data, how = 'right', on = ['Metadata_time', 'Location_Center_X', 
            'Location_Center_Y', 'Metadata_zstep'], sort = False)
        """
        cp_data = cp_data.loc[cp_data['Metadata_zstep'] == 1]

        t_array = cp_track['objects']['obj_type_1']['coords'][:,0]
        x_array = cp_track['objects']['obj_type_1']['coords'][:,1]
        y_array = cp_track['objects']['obj_type_1']['coords'][:,2]
        z_array = cp_track['objects']['obj_type_1']['coords'][:,3]

        cp_t = cp_data['Metadata_time']
        cp_x = cp_data['Location_Center_X']
        cp_y = cp_data['Location_Center_Y']
        cp_z = cp_data['Metadata_zstep']

        index_order = []

        #ordered_cp = np.zeros([len(cp_track['objects']['obj_type_1']['coords']), len(cp_data.columns)])
        #ordered_cp[:] = ""

        for n in range(len(cp_track['objects']['obj_type_1']['coords'])):
            if n%10000 == 0:
                print("At point " + str(n))
            index_t = np.isclose(t_array[n], cp_t).nonzero()
            index_x = np.isclose(x_array[n], cp_x).nonzero()
            index_y = np.isclose(y_array[n], cp_y).nonzero()
            index_z = np.isclose(z_array[n], cp_z).nonzero()
            index_final = set(index_t[0].tolist()) & set(index_x[0].tolist()) & set(index_y[0].tolist()) & set(index_z[0].tolist())
            if len(index_final) == 1:
                #ordered_cp[n,:] = np.array(cp_data.iloc[int(list(index_final)[0])])
                index_order.append(list(cp_data.iloc[int(list(index_final)[0])]))
            else:
                print('ah')
                index_order.append([np.nan]*len(cp_data.columns))
        ordered_cp = pd.DataFrame(index_order, columns = cp_data.columns)

        str_dtype = h5py.string_dtype(encoding='utf-8') 

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
output = Path("/Users/ConradOakes/CellBaum/output")
w = 'XY01'
save = 'all'
add_to_h5(output, w, save)
"""