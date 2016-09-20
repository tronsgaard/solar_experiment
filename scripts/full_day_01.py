#!/usr/bin/env python
# -*- coding: utf-8 -*-
from solar_setup import *

"""
This script runs the SONG solar experiment for a day, using the building blocks
and wrappers defined in solar_setup.py.

-- Written by René Tronsgaard Rasmussen, September 2016
"""

# Initialize the slit guider
init_slitguider(0.01)

# Go to slit 8 (25 µm)
PST.move(settings['slit_motor'], 8)

# TODO: Check that focus is at expected position?

# Run morning calibrations
calib_bias(50)
calib_flat(1.0, 50)
calib_thar(1.0, 3)

# Wait for altitude
wait_for_altitude(30)

# Observe the sun with iodine
observe_sun(1.0, iodine=True,
            condition=lambda: sun_ascending() and sun_below_altitude(80))

# Make template observations
calib_flat(1.0, 10, iodine=True)
observe_sun(1.0, 10, iodine=False)
calib_flat(1.0, 10, iodine=True)

# Observe the sun with iodine
observe_sun(1.0, iodine=True, condition=lambda: sun_above_altitude(30))

# Done for today! Return PST to idle state
IdleMode()
shutdown_slitguider()
