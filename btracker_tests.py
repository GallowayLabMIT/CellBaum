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

# NOTE(arl): This should be from your image segmentation code
objects = ('/Users/ConradOakes/Desktop/Galloway_2021/cell_data/cell_locationsIdentifyPrimaryObjects.csv')
objects = pd.read_csv(objects)

formatted = objects.rename(columns={'Metadata_time' : 't', 'Location_Center_X' : 'x', 
                                    'Location_Center_Y' : 'y', 'Metadata_zstep' : 'z'})
formatted = formatted[['t', 'x', 'y', 'z']]

#formatted['ID'] = formatted.index

objects_to_track = localizations_to_objects(formatted)

# initialise a tracker session using a context manager
with btrack.BayesianTracker() as tracker:

  # configure the tracker using a config file
  tracker.configure_from_file('/Users/ConradOakes/BayesianTracker/models/cell_config.json')
  tracker.update_method = BayesianUpdates.EXACT
  tracker.max_search_radius = 100
  # append the objects to be tracked
  tracker.append(objects_to_track)

  # set the volume (Z axis volume is set very large for 2D data)
  tracker.volume=((0,3700),(0,2800),(0,4))

  # track them (in interactive mode)
  tracker.track_interactive(step_size=2)

  # generate hypotheses and run the global optimizer
  #tracker.optimize()

  # get the tracks as a python list
  tracks = tracker.tracks
  # get the first track
  track_zero = tracks[0]  
  for n in range(len(tracks)):
      if len(tracks[n].children) > 0:
          print("got him")
          break
  generation_q = [n]
  generation_track = []
  while len(generation_q) > 0:
    generation_q.append(tracks[generation_q[0]].children)
    generation_track.append(generation_q[0]-1)
    print(generation_q)
    print(generation_track)
    del generation_q[0]
    
    # print the length of the track
    print(len(track_zero))
    
    # print all of the xyzt positions in the track
    print(track_zero.x)
    print(track_zero.y)
    print(track_zero.z)
    print(track_zero.t)
    
    # print the fate of the track
    print(track_zero.fate)

    # print the track ID, root node, parent node, children and generational depth
    print(track_zero.ID)
    print(track_zero.root)
    print(track_zero.parent)
    print(track_zero.children)
    print(track_zero.generation)
    
    box = tracker.volume
    plot_tracks([track_zero], order='xyt', box=box)
    from btrack.dataio import export_CSV
    # export tracks in CSV format
    export_CSV('/Users/ConradOakes/Desktop/Galloway_2021/bstack_tests/tracks.csv', tracks)
