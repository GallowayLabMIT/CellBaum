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

def btracking(input, cell_config, output):
  # creates objects to track
  objects = input + "/cell_locationsIdentifyPrimaryObjects.csv"
  objects = pd.read_csv(objects)
  formatted = objects.rename(columns={'Metadata_time' : 't', 'Location_Center_X' : 'x', 
                                      'Location_Center_Y' : 'y', 'Metadata_zstep' : 'z'})
  formatted = formatted[['t', 'x', 'y', 'z']]
  objects_to_track = localizations_to_objects(formatted)

  # initialise a tracker session using a context manager
  with btrack.BayesianTracker() as tracker:
    # configure the tracker using a config file
    tracker.configure_from_file(cell_config)
    tracker.update_method = BayesianUpdates.EXACT
    tracker.max_search_radius = 10
    # append the objects to be tracked
    tracker.append(objects_to_track)
    # set the volume (Z axis volume is set very large for 2D data)
    tracker.volume=((0,3700),(0,2800),(0,4))
    # track them (in interactive mode)
    tracker.track_interactive(step_size=1)
    # generate hypotheses and run the global optimizer
    tracker.optimize()
    # get the tracks as a python list
    tracks = tracker.tracks
    # get the first track
    track_zero = tracks[0]  
    for n in range(len(tracks)):
        if len(tracks[n].children) > 0:
            print("got him")
            break
    """
    generation_q = [n]
    generation_track = []
    while len(generation_q) > 0:
      generation_q.append(tracks[generation_q[[0]]].children)
      generation_track.append(generation_q[[0]]-1)
      print(generation_q)
      print(generation_track)
      del generation_q[0] """
    track_good = tracks[n-1]
    # print the length of the track
    print(len(track_good))
    # print all of the xyzt positions in the track
    print(track_good.x)
    print(track_good.y)
    print(track_good.z)
    print(track_good.t)
    # print the fate of the track
    print(track_good.fate)
    # print the track ID, root node, parent node, children and generational depth
    print(track_good.ID)
    print(track_good.root)
    print(track_good.parent)
    print(track_good.children)
    print(track_good.generation)
    # display tracks in 3D space
    box = tracker.volume
    plot_tracks(tracks, order='xyt', box=box)
    # export tracks in CSV format
    export_CSV(output+'/tracks.csv', tracks)

data = '/Users/ConradOakes/Desktop/Galloway_2021/XY01cell_data'
save = "/Users/ConradOakes/Desktop/Galloway_2021/bstack_tests"
cell_configs = '/Users/ConradOakes/BayesianTracker/models/cell_config.json'
btracking(data, cell_configs, save)
