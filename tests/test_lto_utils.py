import os
import sys
import pandas as pd 
from lto_utils.lto_file import LTO_File, getSpectralCharacteristics, getDriftScan

lto_data = './lto_data' # dir with testfiles
obs_dir = '2018_09_02'
obs_file = 'LTO-HI-2018-09-02-10-24-22.lto'

def testinit():
    lto = LTO_File(os.path.join(lto_data, obs_dir,obs_file))
    #did we get a file?
    assert lto.get_time() == pd.Timestamp('2018-09-02 10:24:22+00:00')

def testspecchars():
    #test whether we can read the spec chars for all the lto files in a dir
	lto_obs = getSpectralCharacteristics(os.path.join(lto_data,obs_dir))
	assert len(lto_obs) ==  243


def testdriftscan():
    #test whether we can read up a drift all the lto files in a dir
	ds = getDriftScan(os.path.join(lto_data, obs_dir))
	assert len(ds) ==  3981555