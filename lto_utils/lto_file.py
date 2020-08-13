import numpy as np
import pandas as pd
from struct import *
from collections import OrderedDict

from os import listdir
import re

# empty dictionary to hold the header structure
def init_LTO_File_struct(call_site):

	#print('Initializing file struct: ' + call_site)
	LTO_File_Hdr = OrderedDict()

	# magic number at top of file
	LTO_File_Hdr["Magic"] =  [
		('magic',   int, 'l'),
		('version', int, 'l'),
		('headersize', int, 'l')
	]

	# observatory
	LTO_File_Hdr['Observatory'] = [
		('obs_name', str, '32s'),
		('obs_id',   int, 'l'),
		('ref_type', str, '32s'),
		('clock_type',str,'32s'),
		('rx_type',  str, '32s')
	]

	# obs loc
	#f_obsloc_tup = namedtuple('F_Obsloc_tup',['lat', 'lon', 'alt'])
	#f_obsloc_fmt = '<3f'
	LTO_File_Hdr['ObsLocation'] = [
		('lat', float, 'f'),
		('lon', float, 'f'),
		('alt', float, 'f')
	]

	# beam pos
	LTO_File_Hdr['BeamPosition'] = [
		('az',    float, 'f'),
		('el',    float, 'f'),
		('dec',   float, 'f'),
		('ra',    float, 'f'),
		('user1', str,   '64s')
	]

	#observing time

	LTO_File_Hdr['ObsTime'] = [
		('year',   int, 'l'),
		('daynum', int, 'l'),
		('month',  int, 'l'),
		('day',    int, 'l'),
		('hour',   int, 'l'),
		('minute', int, 'l'),
		('second', float, 'f'),
		('epoch',  int,  'q'), #q = 8 byte int
		('julian', float, 'd'), #d = double maps to python float
		('GST',    float, 'd'),
		('LST',    float, 'd'),
		('readme', str, '128s'),
		('user2',  str, '64s')
	]

	#Spectrum
	LTO_File_Hdr['Spectrum'] =[
		('samplerate',  float, 'f'),
		('wordformat',  int,   'l'),
		('numchannels', int,   'l'),
		('lenfft',      int,   'l'),
		('numspec',     int,   'l'),
		#('numave',      int,   'l'),
		('period',      float, 'f'),
		('dfs',         float, 'f'),
		('cf',          float, 'd'), # 8 byte float
		('nenbw',       float, 'f'),
		('enbw',        float, 'f'),
		('ws1',         float, 'f'),
		('ws2',         float, 'f'),
		('dt',          float, 'f'),
		('flow',		float, 'f'),
		('fhigh', 		float, 'f'),
		('ndlow', 		int, 'l'),
		('ndhigh', 		int, 'l'),
		('user3',       str,   '64s')
	]

	#Radio Calibrations
	LTO_File_Hdr['RadioCalibrations'] = [
		('g0feed',      float, 'f'),
		('g0rx',        float, 'f'),
		('g03',         float, 'f'),
		('feedtemp',    float, 'f'),
		('rxtemp',      float, 'f'),
		('temp3',       float, 'f'),
		('noisefigure', float, 'f'),
		('dgdtf',       float, 'f'),
		('dgdtr',       float, 'f'),
		('dgdt3',       float, 'f'),
		('tsys',        float, 'f'),
		('aeff',        float, 'f'),
		('flatcal',     float, 'f'),
		('pcal',        float, 'f'),
		('gsys',        float, 'd'),
		('user4',       str,   '64s'),
	]

	#Program Control
	LTO_File_Hdr['ProgramControl'] = [
		('fscale',  float,'f'),
		('flat',    bool, 'L'), # read these as 4-byte unsigned longs
		('flattype', int,  'l'),
		('bogie',   bool, 'L'),
		('smooth',  bool, 'L'),
		('nsmooth', int,  'l'),
		('spikes',  bool, 'L'),
		('spiketh', float, 'f'),
		('rmlo',    bool, 'L'),
		('whole',   bool, 'L'),
		('rmqrm',   bool, 'L'),
		('window',  bool, 'L'),
		('winnum',  int,  'l'),
		('overlap', float,'f'),
		('user5',   str,  '64s')
	]

	LTO_File_Hdr['SpectralCharacteristics'] = [

		('avespecpwr', float, 'd'),
		('varspecpwr', float, 'd'),
		('totalpwr',   float, 'd'),
		('numspecpwr', int, 'l'),
		('numave', int, 'l'),
		('numbad', int, 'l'),
		('aveindvpwr', float, 'd'),
		('varindvpwr', float, 'd'),
		('peakpwr', float, 'd'),
		('peakpwrfreq', float, 'd'),
		('totalHIpwr', float, 'd'),
		('numHIpwr', int, 'l'),
		('avecrpwr', float, 'd'),
		('varcrpwr', float, 'd'),
		('numcrpwr', int, 'l'),
		('avetsky', float, 'd'),
		('vartsky', float, 'd'),
		('peaktsky', float, 'd'),
		('peaktskyfreq', float, 'd'),
		('avefluxden', float, 'd'),
		('varfluxden', float, 'd'),
		('peakfluxden', float, 'd'),
		('peakfluxfreq', float, 'd'),
		('badspec', bool, 'L'),
		('processing', str, '64s'),
		('user', str, '64s')
		
	]

	#these guys are all arrays of len = lenfft+1
	LTO_File_Data = [
		('dopfreq',   float, 'd'),
		('rawavepwr', float, 'f'),
		('rawvarpwr', float, 'f'),
		('calavepwr', float, 'f'),
		('flatten',   float, 'f'),
		('tsky',      float, 'f'),
		('fluxden',   float, 'f'),
		('badline',   bool,  'L'), #booleans read as unsigned longs
		('HIline',    bool,  'L')
	]
	return {'Header': LTO_File_Hdr, 'Data':LTO_File_Data}
	
class LTO_File:

	file_struct = init_LTO_File_struct('in class def')
	
	def __init__(self, path, spectralData=True):
		self.initialized = True
		self.path = path
		self.get_SpectralLine(spectralData=spectralData)
	
	def display(self):
		print (self.file_struct)

	def set_path(self, path):
		self.path = path

	def getfilebytes(self, offset, nwords):
		#4 byte words
		with open(self.path,'rb') as fin:
			fin.seek(offset)
			buf = fin.read(nwords*4)
		return buf
		
	def get_SpectralLine(self, spectralData=True, dfclip=None):
		with open(self.path, 'rb') as fin:
			
			# read the file header
			LTO_File_Hdr = LTO_File.file_struct['Header']
			lto_hdr = {}
			for sect in LTO_File_Hdr: # loop thru the sections and read the members of each
				#print ('loading: ' + sect)
				sect_dict = {}
				for f in LTO_File_Hdr[sect]:
					#old bug workaround:
					#if sect=='SpectralCharacteristics' and f[0] == 'processing':
						#fin.seek(1032) #processing field starts here!
					fmt = '<'+ f[2]
					n = calcsize(fmt)
					buf = fin.read(n)
					v = unpack(fmt, buf)[0]
					if f[1] == str:
						v = v.decode('utf8').strip()
					elif f[1] == bool:
						v = bool(v != 0)
					sect_dict[f[0]] = v
					
				lto_hdr[sect] = sect_dict
				

			nelems = lto_hdr['Spectrum']['lenfft'] +1 # each data array is this long
			LTO_File_Data = LTO_File.file_struct['Data']
			lto_data = {}
			if spectralData:
				for d in LTO_File_Data:
					fmt = '<' + str(nelems) + d[2]
					n = calcsize(fmt)
					buf = fin.read(n)
					if d[1] == bool:
						lto_data[d[0]] = (np.array(unpack(fmt, buf)) != 0)
					else:
						lto_data[d[0]] = np.array(unpack(fmt, buf))
						
				# deal with clipping if  needed:
				if dfclip is not None:
					not_clipped = np.logical_and(lto_data['dopfreq'] >= dfclip[0],
												lto_data['dopfreq'] <= dfclip[1]) #these are the keepers
					for d in lto_data:
						lto_data[d] = lto_data[d][not_clipped]
					
			self.SpectralHeader = lto_hdr
			self.SpectralData   = lto_data

			
			
	def get_time(self):
		obs_time = self.SpectralHeader['ObsTime']
		sec = int(obs_time['second'])
		microsec = int((obs_time['second']-sec)*1e6)
		ts = pd.Timestamp(year=obs_time['year'], month=obs_time['month'], day=obs_time['day'],
				hour=obs_time['hour'], minute=obs_time['minute'],
				second=sec, microsecond=microsec,
				tz = 'UTC')
		return ts
				
	def get_radec(self):
		bp = self.SpectralHeader['BeamPosition']
		return {'ra':bp['ra'], 'dec':bp['dec']}
		
	def to_pandas(self):
		radec = self.get_radec()
		ts = self.get_time()
		df = pd.DataFrame({'ts':ts, 'ra':radec['ra'], 'dec':radec['dec'], **self.SpectralData})
		return df
		
	def get_fileoffsets(self):
		hdr_df = pd.DataFrame([(s,v[0], v[1],v[2])  for s in self.file_struct['Header'] for v in self.file_struct['Header'][s]],
					 columns=['Section', 'Field', 'PythonType','Format'])
		hdr_df['FileSize'] = [calcsize('<'+f.Format) for f in hdr_df.itertuples()]
		hdr_df['Offset'] = [0]+hdr_df.FileSize.cumsum()[0:len(hdr_df)-1].tolist()
		return hdr_df

	def bytes2hexwords(self, b):
		#assume 4-byte words
		l = len(b)
		return np.array(['0x'+''.join(['%0*X' % (2,b[j]) for j in range(i,i+4)]) for i in range(0,l,4)])

def __getSpectralData(path, dfclip):
	f = LTO_File()
	f.set_path(path)
	f.get_SpectralLine(dfclip=dfclip)
	return f.to_pandas()
	

def getDriftScan(root, dfclip=None):

	ltofiles = [f for f in listdir(root) if re.search('.*lto$',f) ]
	df = pd.concat([__getSpectralData(root+'/'+f, dfclip=dfclip) \
				for f in ltofiles]).reset_index(drop=True)
	return df

def __getSpectralCharacteristics(path):
	f = LTO_File(path, spectralData=False)

	ts = f.get_time()
	radec = f.get_radec()
	return pd.DataFrame({**radec, **f.SpectralHeader['SpectralCharacteristics']},
	 index=[ts])


def getSpectralCharacteristics(root):
	ltofiles = [f for f in listdir(root) if re.search('.*lto$',f) ]
	df = pd.concat([__getSpectralCharacteristics(root+'/'+f) \
				for f in ltofiles])
	return df


if __name__ == "__main__":

	import os

	lto_data = './lto_data' # dir with testfiles
	obs_dir = '2018_09_02'
	obs_file = 'LTO-HI-2018-09-02-10-24-22.lto'

	print(f'Current working directory: {os.getcwd()}')

	lto = LTO_File(os.path.join(lto_data, obs_dir,obs_file))


	print(lto.SpectralHeader['SpectralCharacteristics'])

	print('getting spectral data')
	lto_obs = getSpectralCharacteristics(os.path.join(lto_data,obs_dir))
	print(f'len of lto_obs: {len(lto_obs)}')