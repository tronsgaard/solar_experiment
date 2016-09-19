import sys
import os
import time
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

    # Calibration slide
    'calibration_motor': 4,
    'calibration_positions': {
        'free': 1,
        'halogen': 2,
        'ThAr': 3,
        'sun': 4,
    },

    # Iodine slide
    'iodine_motor': 3,
    'iodine_positions': {
        'cell2': 1,
        'free': 2,
        'cell1': 3,
    },

    # Beamsplitter slide
    'beamsplitter_motor': 2,
    'beamsplitter_positions': {
        'engineering': 1,
        'acquisition': 2,
        'beamsplitter': 3,
    },

    # Filter wheel
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
}

# Import the pst module, controlling the preslit table motors
sys.path.append(settings['DMC_PATH'])
import pst
PST = pst.PST()


class PreslitTable():
    """Simplified model of preslit table"""

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
        # Move calibration slide
        if self.calibration is not None:
            PST.move(settings['calibration_motor'], self.calibration_pos)
        # Move iodine slide
        if self.iodine_pos is not None:
            PST.move(settings['iodine_motor'], self.iodine_pos)
        # Move beamsplitter slide
        if self.beamsplitter_pos is not None:
            PST.move(settings['bramsplitter_motor'], self.beamsplitter_pos)
        # Move filter wheel
        if self.filter_pos is not None:
            PST.move(settings['filter_motor'], self.filter_pos)

        # ThAr lamp
        if self.thar_lamp is True:
            os.system(DMC_PATH + "/lamp.py thar on")  # Turn on the ThAr lamp
            time.sleep(1)
        elif self.thar_lamp is False:
            os.system(DMC_PATH + "/lamp.py thar off")  # Turn off the ThAr lamp
            time.sleep(1)

        # Halogen lamp
        if self.halogen_lamp is True:
            os.system(DMC_PATH + "/lamp.py halo on")  # Turn on the halogen lamp
            time.sleep(1)
        elif self.halogen_lamp is False:
            os.system(DMC_PATH + "/lamp.py halo off")  # Turn off the halogen lamp
            time.sleep(1)

        # Set M8 position to idle???  # FIXME: Check what this script does
        Set_M8.set_m8_pos()


    def get_state(self):
        """Get the current state of the preslit table"""
        # Get calibration slide position
        where = PST.where(settings['calibration_motor'])
        if where[0] is None:
            raise Error('The calibration slide is at an undefined position')
        else:
            self.calibration_pos = where[0]

        # Get iodine slide position
        where = PST.where(settings['iodine_motor'])
        if where[0] is None:
            raise Error('The iodine slide is at an undefined position')
        else:
            self.iodine_pos = where[0]

        # Get beamsplitter slide position
        where = PST.where(settings['beamsplitter_motor'])
        if where[0] is None:
            raise Error('The beamsplitter slide is at an undefined position')
        else:
            self.beamsplitter_pos = where[0]

        # Get filter wheel position
        where = PST.where(settings['filter_motor'])
        if where[0] is None:
            raise Error('The filter wheel is at an undefined position')
        else:
            self.filter_pos = where[0]

        # TODO: Get lamps


class ThArMode(PreSlitTable):
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


###############################################################################

# Wrap system calls

def init_slitguider(texp=0.01):
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
    os.system(settings['SLIT_PATH'] + "/sigu.py texp %d" % texp)


def shutdown_slitguider():
    os.system(settings['SLIT_PATH'] + "/slit_guider.py -t")  # Stop the slit guider


def ccd_acquire(texp, imtype, objname, ra=None, dec=None)
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
        command += " --obj_ra=%s --obj_dev=%s"  # Format xx:xx:xx
    # Fire the command
    os.system(command)


###############################################################################

# Define building blocks for the observation

def calib_bias(nexp, return_pst=True):
    """
    Make nexp bias exposures and return PST to previous state.
    """
    # Set the PST to bias mode
    BiasMode().set_state()
    # Take exposures
    for i in range(nexp):
        ccd_acquire(0.0, 'BIAS', 'BIAS')


def calib_flat(nexp, exptime, iodine=False):
    """
    Make nexp halogen flats and return PST to previous state.
    If iodine = True, the iodine cell is rolled in place
    """
    # Set the PST to Flat/FlatI2 mode and take exposures
    if iodine:
        FlatI2Mode().set_state()
        for i in range(nexp):
            ccd_acquire(0.0, 'FLATI2', 'FLATI2')
    else:
        FlatMode().set_state()
        for i in range(nexp):
            ccd_acquire(0.0, 'FLAT', 'FLAT')


def calib_thar(nexp, exptime, return_pst=True):
    """
    Make nexp ThAr exposures and return PST to previous state.
    """
    # Set the PST to bias mode
    ThArMode().set_state()
    # Take exposures
    for i in range(nexp):
        ccd_acquire(0.0, 'THAR', 'THAR')


def observe_sun(nexp, exptime, stop_before=None, iodine=False):
    """
    Make nexp exposures through the sun fiber and return PST to previous state.
    If iodine = True, the iodine cell is rolled in place
    """
    # Calculate current position of the sun
    # TODO
    # Set the PST to Sun/SunI2 mode and take exposures
    if iodine:
        SunI2Mode().set_state()
        for i in range(nexp):
            ccd_acquire(0.0, 'SUNI2', 'SUNI2')  # FIXME: RA/Dec
    else:
        SunMode().set_state()
        for i in range(nexp):
            ccd_acquire(0.0, 'SUN', 'SUN')  # FIXME: RA/Dec

