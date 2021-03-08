#!/global/homes/m/mabitbol/.conda/envs/myenv/bin/python
import numpy as np
import os
import healpy as hp
from combine_noise import compute_noise_factors, combine_noise_maps

"""
Script to combine Nicoletta's simulations into observed sky splits. 
Will save a signal only file called SO_SAT_maps_sky_signal.fits
and also save 4 obs splits called SO_SAT_obs_map_split_kof4.fits
All maps are saved as healpix fits files with 18 maps, corresponding to TQU for 6 frequencies. 
Use .reshape(6, 3, -1) to get into frequency, TQU, npix shape. 
DO NOT USE T. 
"""

# Globals
nside = 512
freq_labels = ['27', '39', '93', '145', '225', '280']
fgnames = ['synch', 'dust']
realsims = ['d0s0', 'd1s1', 'dmsm']
fdir = '/global/cfs/cdirs/sobs/users/krach/BBSims/'

def get_sky_signals(nrs, gauss_or_real, pysm_ver=None):
    skymaps = np.zeros((6, 3, hp.nside2npix(nside)))
    for k, fl in enumerate(freq_labels): 
        fname = f'{fdir}CMB_r0_20201207/cmb/{nrs}/SO_SAT_{fl}_cmb_{nrs}_CMB_r0_20201207.fits'
        skymaps[k] += hp.read_map(fname, field=range(3), verbose=False)
        for fgn in fgnames:
            if gauss_or_real == 'gauss':
                fname = f'{fdir}FG_20201207/gaussian/foregrounds/{fgn}/{nrs}/SO_SAT_{fl}_{fgn}_{nrs}_gaussian_20201207.fits'
            else: 
                fname = f'{fdir}FG_20201207/realistic/{pysm_ver}/foregrounds/{fgn}/SO_SAT_{fl}_{fgn}_{pysm_ver}_20201207.fits'
            skymaps[k] += hp.read_map(fname, field=range(3), verbose=False)
    return skymaps

def get_noise(nrs, sensitivity_mode, one_over_f):
    factors = compute_noise_factors(sensitivity_mode, one_over_f)
    noisemaps = np.zeros((6, 3, hp.nside2npix(nside)))
    for k, fl in enumerate(freq_labels): 
        noisemaps[k] = combine_noise_maps(nrs, int(fl), factors)
    return noisemaps

def get_path(sdir, nrs, sensitivity_mode, one_over_f, gauss_or_real, pysm_ver=None):
    if gauss_or_real == 'gauss':
        path = os.path.join(sdir, 'gaussian')
    else:
        path = os.path.join(sdir, 'realistic')
        assert(pysm_ver in realsims)
        path = os.path.join(path, pysm_ver)

    if sensitivity_mode == 1: 
        path = os.path.join(path, 'baseline')
    else: 
        path = os.path.join(path, 'goal')

    if one_over_f is None: 
        path = os.path.join(path, 'white')
    elif one_over_f == 0: 
        path = os.path.join(path, 'pessimistic')
    else:   
        path = os.path.join(path, 'optimistic')

    path = os.path.join(path, nrs, '')

    try:
        os.mkdir(path)
    except:
        pass
    print(path)
    return path

def run(sdir, nr, sensitivity_mode, one_over_f, gauss_or_real, pysm_ver=None, overwrite=True):
    """ Create signal maps and obs sky maps for all 6 SO frequencies. Write to disk. 
        example params: 
        sdir = 'test/'                  # directory to save sims
        nr = 0                          # realization number 0-500. 
        sensitivity_mode = 2            # noise sensitivity mode: 1 baseline, 2 goal
        one_over_f = None               # one over f: None no 1/f, 0 pessimistic 1/f, 1 optimistic 1/f
        gauss_or_real = 'gauss'         # 'gauss' or 'real' for FG simulation type
        pysm_ver = None                 # FG pysm version, required for 'real' FG sims. Choose from 'd0s0', 'd1s1', or 'dmsm'.
        overwrite = True                # overwrite existing files
    """
    nrs = str(nr).zfill(4)
    sdir = get_path(sdir, nrs, sensitivity_mode, one_over_f, gauss_or_real, pysm_ver)
    skymaps = get_sky_signals(nrs, gauss_or_real, pysm_ver)
    sname = f'{sdir}SO_SAT_maps_sky_signal.fits'
    hp.write_map(sname, skymaps.reshape(18, -1), overwrite=overwrite)
    for k in range(4):
        nrx = nr + k*500
        nrxs = str(nrx).zfill(4)
        noisemaps = get_noise(nrxs, sensitivity_mode, one_over_f)
        sname = f'{sdir}SO_SAT_obs_map_split_{k+1}of4.fits'
        totalmaps = noisemaps + skymaps
        hp.write_map(sname, totalmaps.reshape(18, -1), overwrite=overwrite)
    return 

#sdir = '/global/cfs/cdirs/sobs/users/mabitbol/sims'
#gauss_or_real = 'gauss'
#pysm_ver = None
#overwrite = True
#for k in range(500):
#    for sensitivity_mode in [1, 2]:
#        for one_over_f in [None, 0, 1]:
#            run(sdir, k, sensitivity_mode, one_over_f, gauss_or_real, pysm_ver, overwrite)

sdir = '/global/cfs/cdirs/sobs/users/mabitbol/sims'
gauss_or_real = 'real'
overwrite = True
for k in range(249, 500):
    for pysm_ver in realsims:
        for sensitivity_mode in [1, 2]:
            for one_over_f in [None, 0, 1]:
                run(sdir, k, sensitivity_mode, one_over_f, gauss_or_real, pysm_ver, overwrite)



