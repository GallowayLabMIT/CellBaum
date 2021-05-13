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
#import napari
import numpy as np


def btracking(input, cell_config, output, well, t_scales, min_t):
  # creates objects to track
  objects = input + "/cell_locationsIdentifyPrimaryObjects.csv"
  objects = pd.read_csv(objects)
  formatted = objects.rename(columns={'Metadata_time' : 't', 'Location_Center_X' : 'x', 
                                      'Location_Center_Y' : 'y', 'Metadata_zstep' : 'z'})
  formatted = formatted[['t', 'x', 'y', 'z']]
  formatted = formatted[formatted['z'] == 1]
  objects_to_track = localizations_to_objects(formatted)

  # initialise a tracker session using a context manager
  with btrack.BayesianTracker() as tracker:
    # configure the tracker using a config file
    tracker.configure_from_file(cell_config)
    tracker.update_method = BayesianUpdates.EXACT
    tracker.max_search_radius = 100
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
    #get cell velocities
    v_track = []
    for cell in tracks:
      v_track += [find_cell_velocity(cell, t_scales, min_t)]
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
    # export tracks in h5 format and velocities in csv format
    tracker.export(output+'/'+well+'tracks.h5', obj_type='obj_type_1')
    v_track = pd.DataFrame({'velocity':v_track})
    v_track.to_csv(output+'/'+well+'_velocity.csv')

def find_cell_velocity(track, t_scale=1, t_min=2):
  #if there are not enough points to calculate movement, returns NA
  if len(track.t) <= 1 or len(track.t) < t_min:
    return np.nan
  else:
    x_vals = track.x
    y_vals = track.y
    z_vals = track.z
    t_vals = track.t
    vel = []
    # for every sequential set of points, calculates distance between them
    for point in range(len(x_vals)-1):
      x = ((x_vals[point])-(x_vals[point+1]))**2
      y = ((y_vals[point])-(y_vals[point+1]))**2
      z = ((z_vals[point])-(z_vals[point+1]))**2
      t = abs((t_vals[point])-(t_vals[point+1]))
      d = np.sqrt(x+y+z)
      vel += [d/(t*t_scale)]
    # averages the velocities of all sequential sets of points
    v = sum(vel)/len(vel)
    return v
  
"""
data = '/Users/ConradOakes/Desktop/Galloway_2021/XY02cell_data'
save = "/Users/ConradOakes/Desktop/Galloway_2021/bstack_tests"
cell_configs = '/Users/ConradOakes/BayesianTracker/models/cell_config.json'
well = 'XY02'
btracking(data, cell_configs, save, well, 15, 2)
"""