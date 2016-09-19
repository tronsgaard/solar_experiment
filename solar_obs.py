#!/usr/bin/python
from solar_setup import *

"""
This script runs the SONG solar experiment for a day, using the building blocks
and wrappers defined in solar_setup.py.

-- Written by René Tronsgaard Rasmussen, September 2016
"""

# Save the current PST setup
pst_before = PreSlitTableState().get_state()

# Go to slit 8
pst.move(settings['slit_motor'], 8)

# TODO: Check that focus is at expected position?

# Run morning calibrations
calib_bias(50, return_pst=False)
calib_flat(50, 1.0, return_pst=False)
calib_thar(3, 1.0, return_pst=False)

# Initialize the slit guider
init_slitguider(0.001)

# Observe the sun with iodine
observe_sun(0, 1.0, iodine=True, stop_before='14:00', return_pst=False)

# Make template observations
calib_flat(10, 1.0, iodine=True, return_pst=False)
observe_sun(10, 1.0, iodine=False, return_pst=False)
calib_flat(10, 1.0, iodine=True, return_pst=False)

# Observe the sun with iodine
observe_sun(0, 1.0, iodine=True, stop_before='18:00', return_pst=False)

# Done for today! Return PST to previous state
pst_before.set_state()
shutdown_slitguider()