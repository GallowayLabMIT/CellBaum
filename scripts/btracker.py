#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 08:31:19 2021

@author: ConradOakes
"""
import btrack
from btrack.constants import BayesianUpdates
from btrack.dataio import localizations_to_objects
from btrack.render import plot_tracks
import pandas as pd
from btrack.dataio import export_CSV
from pathlib import Path
from PIL import Image
#import napari

def get_image_dims(input_dir):
  dimx = []
  dimy = []
  for file in Path(input_dir).rglob("*.tif"):
    im = Image.open(file).convert("L")
    dimx += [im.size[0]]
    dimy += [im.size[1]]
  return dimx, dimy

"""
Uses BTracker to generate h5 files of cell tracks. 
Parameters
----------
input_csv: Path
  The path to the file containing CellProfiler-exported data.
cell_config: Path
  The path to json with the cell_config model
output_file: Path
  The path to the output h5 file write
update: str
  Either 'EXACT' or 'APPROXIMATE' (default 'EXACT')
z_filter: int
  The z level to filter by (default = 1)
search: int
  The minimum search distance (default = 100)
volume: Tibble of tibbles of ints
  The size of the area being tracked
step: int
  The time step for tracking
Returns
-------
None
"""
def btracking(input_csv:Path, cell_config:Path, output_file:Path, update:str = 'EXACT', 
  z_filter:int = 1, search:int = 100, vol = ((0,3700),(0,2800),(0,4)), step:int = 1, log_file = None)->None:
  # creates objects to track
  #objects = Path(input) / "cell_locationsIdentifyPrimaryObjects.csv"
  objects = pd.read_csv(input_csv)
  if 'Metadata_zstep' not in objects.columns:
    objects['Metadata_zstep'] = 1
  formatted = objects.rename(columns={'Metadata_time' : 't', 'Location_Center_X' : 'x', 
                                      'Location_Center_Y' : 'y', 'Metadata_zstep' : 'z'})
  formatted = formatted[['t', 'x', 'y', 'z']]
  formatted = formatted[formatted['z'] == z_filter]
  objects_to_track = localizations_to_objects(formatted)
  # initialise a tracker session using a context manager
  with btrack.BayesianTracker() as tracker:
    # configure the tracker using a config file
    tracker.configure_from_file(Path(cell_config))
    if update == 'EXACT':
      tracker.update_method = BayesianUpdates.EXACT
    else:
      tracker.update_method = BayesianUpdates.APPROXIMATE
    tracker.max_search_radius = search
    # append the objects to be tracked
    tracker.append(objects_to_track)
    # set the volume (Z axis volume is set very large for 2D data)
    tracker.volume= vol
    # track them (in interactive mode)
    tracker.track_interactive(step_size=step)
    # generate hypotheses and run the global optimizer
    tracker.optimize()
    """
    # Below used for visualizing in napari
    gen = 0
    counter = 0
    persist = 0
    print(len(tracks))
    for n in range(len(tracks)):
      if (len(tracks[n].x)) > len(tracks[persist].x):
        persist = n
      if (tracks[n].generation) > 0:
        counter +=1
      if (tracks[n].generation) > gen:
        gen = tracks[n].generation
        print(gen)
        print(n)
        the_n = n
  
    tracks_cut = [tracks[the_n]]
    start = [tracks[the_n]]
    while len(start) > 0:
      for track in tracks:
        if (track.parent) == start[0].ID:
          break
        elif track.ID == start[0].parent:
          tracks_cut += [track]
          start += [track]
          print(start)
          print(track)
      del start[0]
    print(tracks_cut)

    box = tracker.volume
    plot_tracks(tracks_cut, order='xyt', box=box)
    plot_tracks(tracks, order='xyt', box=box)
    plot_tracks([tracks[persist]], order='xyt', box=box)

    # optional: get the data in a format for napari
    data, properties, graph = tracker.to_napari(ndim=2)
    napari.view_tracks(data, properties=properties, graph=graph, name = 'Tracks')
    napari.run()
    """
    # export tracks in h5 formats
    tracker.export(str(output_file), obj_type='obj_type_1')
  
"""
data = Path('/Users/ConradOakes/CellBaum/output/XY01cell_data/cell_locationsIdentifyPrimaryObjects.csv')
save = Path("/Users/ConradOakes/CellBaum/output/btrack_results/XY01tracks.h5")
cell_configs = Path('/Users/ConradOakes/BayesianTracker/models/cell_config.json')
well = 'XY01'
btracking(data, cell_configs, save, well)
"""
#print(get_image_dims(Path("/Users/ConradOakes/CellBaum/output/stitched/XY01")))

