#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
from datetime import datetime, timedelta
import ephem
import Set_M8

"""
This module sets up the SONG solar experiment, providing building blocks
and wrappers for simplified observing scripts.

-- Written by René Tronsgaard Rasmussen, September 2016
"""

settings = {

    # Paths to motor controller and Andor CCD programs.
    'DMC_PATH': '/home/obs/programs/DMC',
    'ANDOR_PATH': '/home/madsfa/subversion/trunk/spec_ccd',
    'SLIT_PATH': '/home/obs/programs/guiders/slit',

    # CCD parameters
    'ccd_pre_amp_gain': 2,  # [0,1,2]   = [x1, x2, x4]
    'ccd_readoutspeed': 1,  # [0,1,2,3] = [5MHz, 3MHz, 1MHz, 0.05MHz]
    'ccd_daynight': 'sun',  # Leaves images in /scratch/sun_spec/DATE/raw/

    # Calibration slide definition
    'calibration_motor': 4,
    'calibration_positions': {
        'free': 1,
        'halogen': 2,
        'ThAr': 3,
        'sun': 4,
    },

    # Iodine slide definition
    'iodine_motor': 3,
    'iodine_positions': {
        'cell2': 1,
        'free': 2,
        'cell1': 3,
    },

    # Beamsplitter slide definition
    'beamsplitter_motor': 2,
    'beamsplitter_positions': {
        'engineering': 1,
        'acquisition': 2,
        'beamsplitter': 3,
    },

    # Filter wheel definition
    'filter_motor': 1,
    'filter_positions': {
        'ND1': 1,
        'ND2': 2,
        'ND3': 3,
        'free': 4,  # Default
        'free2': 5,
        'ND0.7': 6,
    },

    # Other motors
    'slit_motor': 6,
    'focus_motor': 5,

    # Site coordinates
    'site_lat': 28.2983,
    'site_long': -16.5094,  # East longitude
    'site_elev': 2400.0
}

_pi = 3.141592653589793


# Import the pst module, controlling the preslit table motors
sys.path.append(settings['DMC_PATH'])
import pst
PST = pst.PST()


class PreslitTable():
    """Simplified model of preslit table"""

    def __init__(self):
        # Set defined state when instance is created
        self.set_state()

    # Motor positions (None means ignore)
    calibration_pos = None
    iodine_pos = None
    beamsplitter_pos = None
    filter_pos = None

    # Lamp states (True is on, False is off, None is ignore)
    thar_lamp = None
    halogen_lamp = None

    def set_state(self):
        """Set the preslit table to the state defined by the positions above"""
        print "Setting the PST state to %s..." % self.__class__.__name__
        # Move calibration slide
        if self.calibration_pos is not None:
            PST.move(settings['calibration_motor'], self.calibration_pos)
        # Move iodine slide
        if self.iodine_pos is not None:
            PST.move(settings['iodine_motor'], self.iodine_pos)
        # Move beamsplitter slide
        if self.beamsplitter_pos is not None:
            PST.move(settings['beamsplitter_motor'], self.beamsplitter_pos)
        # Move filter wheel
        if self.filter_pos is not None:
            PST.move(settings['filter_motor'], self.filter_pos)

        # ThAr lamp
        if self.thar_lamp is True:
            os.system(settings['DMC_PATH'] + "/lamp.py thar on")  # Turn on
            time.sleep(1)
        elif self.thar_lamp is False:
            os.system(settings['DMC_PATH'] + "/lamp.py thar off")  # Turn off
            time.sleep(1)

        # Halogen lamp
        if self.halogen_lamp is True:
            os.system(settings['DMC_PATH'] + "/lamp.py halo on")  # Turn on
            time.sleep(1)
        elif self.halogen_lamp is False:
            os.system(settings['DMC_PATH'] + "/lamp.py halo off")  # Turn off
            time.sleep(1)

        # Set M8 position to match PST configuration
        Set_M8.set_m8_pos()

    def get_state(self):
        """Get the current state of the preslit table"""
        # Get calibration slide position
        where = PST.where(settings['calibration_motor'])
        if where[0] is None:
            raise Exception('The calibration slide is at an undefined position')
        else:
            self.calibration_pos = where[0]

        # Get iodine slide position
        where = PST.where(settings['iodine_motor'])
        if where[0] is None:
            raise Exception('The iodine slide is at an undefined position')
        else:
            self.iodine_pos = where[0]

        # Get beamsplitter slide position
        where = PST.where(settings['beamsplitter_motor'])
        if where[0] is None:
            raise Exception('The beamsplitter slide is at an undefined position')
        else:
            self.beamsplitter_pos = where[0]

        # Get filter wheel position
        where = PST.where(settings['filter_motor'])
        if where[0] is None:
            raise Exception('The filter wheel is at an undefined position')
        else:
            self.filter_pos = where[0]

        # TODO: Get lamps, for now just assume they were turned off
        self.thar_lamp = False
        self.halogen_lamp = False


class ThArMode(PreslitTable):
    calibration_pos = settings['calibration_positions']['ThAr']
    iodine_pos = settings['iodine_positions']['cell1']
    beamsplitter_pos = settings['beamsplitter_positions']['beamsplitter']
    filter_pos = None

    thar_lamp = True
    halogen_lamp = False


class FlatMode(PreslitTable):
    calibration_pos = settings['calibration_positions']['halogen']
    iodine_pos = settings['iodine_positions']['free']
    beamsplitter_pos = settings['beamsplitter_positions']['beamsplitter']
    filter_pos = None

    thar_lamp = False
    halogen_lamp = True


class FlatI2Mode(PreslitTable):
    calibration_pos = settings['calibration_positions']['halogen']
    iodine_pos = settings['iodine_positions']['cell1']
    beamsplitter_pos = settings['beamsplitter_positions']['beamsplitter']
    filter_pos = None

    thar_lamp = False
    halogen_lamp = True


class BiasMode(PreslitTable):
    calibration_pos = None
    iodine_pos = None
    beamsplitter_pos = None
    filter_pos = None

    thar_lamp = False
    halogen_lamp = False


class SunMode(PreslitTable):
    calibration_pos = settings['calibration_positions']['sun']
    iodine_pos = settings['iodine_positions']['free']
    beamsplitter_pos = settings['beamsplitter_positions']['beamsplitter']
    filter_pos = settings['filter_positions']['free']

    thar_lamp = False
    halogen_lamp = False


class SunI2Mode(PreslitTable):
    calibration_pos = settings['calibration_positions']['sun']
    iodine_pos = settings['iodine_positions']['cell1']
    beamsplitter_pos = settings['beamsplitter_positions']['beamsplitter']
    filter_pos = settings['filter_positions']['free']

    thar_lamp = False
    halogen_lamp = False


class IdleMode(PreslitTable):
    calibration_pos = settings['calibration_positions']['free']
    iodine_pos = settings['iodine_positions']['free']
    beamsplitter_pos = settings['beamsplitter_positions']['beamsplitter']
    filter_pos = settings['filter_positions']['free']

    thar_lamp = False
    halogen_lamp = False


###############################################################################

# Wrap system calls

def init_slitguider(texp=0.01):
    print "Attempting to stop and start the slit_guider daemon..."
    # Stop the slit guider and wait till it is initialized
    os.system(settings['SLIT_PATH'] + "/slit_guider.py -t")
    os.system("sleep 5")
    # Start the slit guider and wait
    os.system(settings['SLIT_PATH'] + "/slit_guider.py -s")
    os.system("sleep 5")
    # Do not enable the guiding
    os.system(settings['SLIT_PATH'] + "/sigu.py pause")
    os.system("sleep 2")
    # Start showing the image
    os.system(settings['SLIT_PATH'] + "/sigu.py start")
    # Set the exposure time value
    os.system(settings['SLIT_PATH'] + "/sigu.py texp manual")
    os.system(settings['SLIT_PATH'] + "/sigu.py texp %f" % texp)


def shutdown_slitguider():
    print "Attempting to stop the slit_guider daemon..."
    os.system(settings['SLIT_PATH'] + "/slit_guider.py -t")  # Stop slit guider


def ccd_acquire(texp, imtype, objname, ra=None, dec=None):
    print "Taking CCD exposure of {:.2f} seconds...".format(texp)
    command = "%s/c_acq.py -p%i -r%i -e%f -t%s -o%s --daynight=%s" % (
        settings['ANDOR_PATH'],
        settings['ccd_pre_amp_gain'],
        settings['ccd_readoutspeed'],
        texp,
        imtype,
        objname,
        settings['ccd_daynight'])
    # Set object coordinates
    if ra is not None and dec is not None:
        command += " --obj_ra=%s --obj_dec=%s"  # Format xx:xx:xx
    # Fire the command
    os.system(command)


###############################################################################

# Define building blocks for the observation

def calib_bias(nexp=1):
    """
    Make nexp bias exposures.
    """
    # Set the PST to bias mode
    BiasMode()
    # Take exposures
    for i in range(nexp):
        print 'Taking bias frame %d of %d' % (i+1, nexp)
        ccd_acquire(0.0, 'BIAS', 'BIAS')


def calib_flat(exptime, nexp=1, iodine=False):
    """
    Make nexp halogen flats of exptime seconds.
    If iodine = True, the iodine cell is rolled in place
    """
    # Set the PST to Flat/FlatI2 mode
    if iodine:
        FlatI2Mode()
        imtype = 'FLATI2'
    else:
        FlatMode()
        imtype = 'FLAT'
    # Take exposures
    for i in range(nexp):
        ccd_acquire(exptime, imtype, imtype)


def calib_thar(exptime, nexp=1):
    """
    Make nexp ThAr exposures.
    """
    # Set the PST to bias mode
    ThArMode()
    # Take exposures
    for i in range(nexp):
        ccd_acquire(exptime, 'THAR', 'THAR')


def observe_sun(exptime, nexp=1, condition=None, iodine=False):
    """
    Make nexp exposures through the sun fiber. If iodine = True, the iodine
    cell is rolled in place.
    """
    # Prepare preslit table
    if iodine:
        SunI2Mode()
        imtype = 'SUNI2'
    else:
        SunMode()
        imtype = 'SUN'

    # Get pyephem object for sun
    sun = ephem.Sun()

    def take_sun_exposure():
        # Calculate RA/Dec at mid exposure
        midtime = datetime.utcnow() + timedelta(seconds=exptime)
        sun.compute(midtime)
        # Take exposure
        ccd_acquire(exptime, imtype, imtype, ra=str(sun.ra), dec=str(sun.dec))

    # Main loop
    # If condition is callable, loop as long as condition returns True
    if callable(condition):
        while condition():
            take_sun_exposure()
    # Otherwise, take nexp exposures
    else:
        for i in range(nexp):
            take_sun_exposure()


def _get_ephem():
    # Define pyephem observer
    obs = ephem.Observer()
    obs.lat = str(settings['site_lat'])
    obs.long = str(settings['site_long'])
    obs.elev = settings['site_elev']

    # Get pyephem object for sun
    sun = ephem.Sun()
    sun.compute(obs)

    return obs, sun


def sun_ascending():
    """
        Return True if the sun is ascending
    """
    obs, sun = _get_ephem()
    now = datetime.utcnow()

    if obs.next_transit(sun, now) < obs.next_antitransit(sun, now):
        return True
    else:
        return False


def sun_descending():
    """
        Return True if the sun is descending
    """
    if sun_ascending():
        return False
    else:
        return True


def wait_for_altitude(min_altitude):
    """Hold the prompt until the sun has reached min_altitude (degrees)"""
    obs, sun = _get_ephem()

    # Stop waiting if the sun is descending
    if sun_ascending():
        return

    # Wait if altitude is below min_altitude
    while sun.alt < min_altitude / _pi * 180.:
        print 'Waiting for the sun to reach altitude %f degrees' % min_altitude
        time.sleep(20)
        # Update the sun
        obs.date = datetime.utcnow()
        sun.compute(obs)


def sun_above_altitude(altitude):
    """
        Return True if the sun is above altitude (degrees).
    """
    obs, sun = _get_ephem()

    if sun.alt / _pi * 180. > altitude:
        return True
    else:
        return False


def sun_below_altitude(altitude):
    """
        Return True if the sun is below altitude (degrees).
    """
    if sun_above_altitude(altitude):
        return False
    else:
        return True
