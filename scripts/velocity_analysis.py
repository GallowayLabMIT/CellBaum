import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn
import h5py

"""
Calculates average velocity of a cell along its track.

cell_data: the track's txyz data
t_scale: the units of time being used
t_min: minimum points in time that should be in the track's data to calculate velocity
"""
def find_velocity(cell_data, t_scale=1, t_min = 2):
  v_temp = []
  if cell_data.shape[0] > 2 and cell_data.shape[0] > t_min: 
    for id in range(cell_data.shape[0]-1):
      pointA = cell_data[id,]
      pointB = cell_data[id+1,]
      t = abs((pointA[0])-(pointB[0]))
      x = ((pointA[1])-(pointB[1]))**2
      y = ((pointA[2])-(pointB[2]))**2
      z = ((pointA[3])-(pointB[3]))**2
      d = np.sqrt(x+y+z)
      v_temp += [d/(t*t_scale)] 
    v = sum(v_temp)/len(v_temp)
    return v

"""
Calculates the velocities of every cell track in the provided well

data: folder with h5 data
well: well being examined
t_scaling: the units of time being used
min_t: minimum points in time that should be in the track's data to calculate velocity
"""
def well_to_vel(data, well, t_scaling = 1, min_t = 2):
  #get cell velocities
  v_track = h5py.File(data + '/' + well+'tracks.h5')
  #gets more convenient names for dataframes in the h5 file
  objects = v_track['objects']['obj_type_1']
  tracks = v_track['tracks']['obj_type_1']
  map = tracks['map']
  convert = tracks['tracks']
  cells = objects['coords']
  dummies = tracks['dummies']
  vel = []
  # for each track, gets all relevant object points
  for row in map:
    cell_ids = convert[row[0]:row[1],]
    obj_ids = []
    dummy_ids = []
    for n in cell_ids:
      if n >= 0:
        obj_ids += [n]
      else:
        dummy_ids += [-(n+1)]
    cell_coords = np.empty(shape = (0,5))
    for n in obj_ids:
      cell_coords = np.vstack((cell_coords, cells[n,]))
    for n in dummy_ids:
      cell_coords = np.vstack((cell_coords, dummies[n,]))
    cell_coords = np.sort(cell_coords, axis = 0)
    # calculates average velocity of the track
    vel += [find_velocity(cell_coords, t_scale = t_scaling, t_min = min_t)]
  return vel
 

well_list = ['XY01', 'XY02', 'XY03', 'XY04']
type_list = ['None', '6F', '6FDD', '6FDDRR']
data = {}
dir = "/Users/ConradOakes/CellBaum/output/btrack_results/"

for well in range(len(well_list)):
    data[type_list[well]] = well_to_vel(dir, well_list[well], t_scaling = 15, min_t = 5)

data = pd.DataFrame.from_dict(data, orient = 'index')
data = data.transpose()
data = data.fillna(value=np.nan)
fig, axes = plt.subplots()
violin = seaborn.violinplot(data = data)
violin.set(ylabel = 'Velocity')
plt.show()
