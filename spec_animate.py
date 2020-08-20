from lto_utils.lto_file import LTO_File

class Scope:
	def __init__(self, ax, obs):
		self.ax = ax
		self.obs = obs
		self.keys = list(obs.keys())
		self.first_key=self.keys[0]
		self.last_key = self.keys[-1]
		self.nobs = len(obs)
		self.obs_count = -1
		self.dopfreq = obs[self.first_key]['dopfreq']
		self.tsky = obs[self.first_key]['tsky']
		self.line = Line2D(self.dopfreq, self.tsky)
		self.ax.add_line(self.line)
		#self.ax.set_ylim(100, 170)
		self.ax.set_title('initializing')
		self.ax.set_xlabel('Doppler Frequency (Hz)')
		self.ax.set_ylabel('Sky Temp (K)')
		self.ax.grid(s)
		self.ax.figure.canvas.draw()
		#self.ax.set_xlim(0, self.maxt)

	def update(self, o):
		#lastt = self.tdata[-1]
		#if lastt > self.tdata[0] + self.maxt:  # reset the arrays
		#    self.tdata = [self.tdata[-1]]
		#    self.ydata = [self.ydata[-1]]
		#    self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
		#    self.ax.figure.canvas.draw()

		#t = self.tdata[-1] + self.dt
		self.dopfreq = self.obs[o]['dopfreq']
		self.tsky = self.obs[o]['tsky']
		self.obs_count += 1
		self.line.set_data(self.dopfreq, self.tsky)
		self.ax.set_ylim(100, 170)
		self.ax.set_xlim(self.dopfreq.min(), self.dopfreq.max())
		self.ax.set_title(f'In Update: {o}')
		self.ax.figure.canvas.draw()
		return self.line,



if __name__ == '__main__':
	import argparse
	import re
	import os
	import matplotlib.pyplot as plt
	import matplotlib.animation as animation
	from matplotlib.lines import Line2D

	parser = argparse.ArgumentParser(description='Show spectral lines of a set of observations')
	parser.add_argument('--data_dir',help='where the data is to be found', default='./data')
	parser.add_argument('--dfclip', help = 'doppler freq clip values in Hz of form lo,hi', default='0.25e6,0.75e6')

	args = parser.parse_args()

	print(f'Data dir: {args.data_dir}')
	print(f'dfclip: {args.dfclip}')

	clips = args.dfclip.split(',')
	dfclip_lo = float(clips[0])
	dfclip_hi = float(clips[1])

	print(f'dfclip_lo = {dfclip_lo}, dfclip_hi: {dfclip_hi}')

	#get the lto files in the obs dir
	ltofiles = [f for f in os.listdir(args.data_dir) if re.search('.*lto$',f) ]
	ltofiles.sort()

	#get skytemp from each lto file:
	skytemps = {}
	for l in ltofiles:
		lto_file = LTO_File(os.path.join(args.data_dir, l))
		s = lto_file.dfclipper( dfclip=(dfclip_lo, dfclip_hi))
		skytemps[l] = {'dopfreq':lto_file.SpectralData['dopfreq'][s],
						'tsky':    lto_file.SpectralData['tsky'][s]}

	print(f'Len SkyTemps: {len(skytemps)}')


	fig = plt.figure(figsize=(12,9))
	ax = fig.add_subplot()

	scope = Scope(ax, skytemps)


	anim = animation.FuncAnimation(fig, scope.update, frames=ltofiles,interval=20,blit=True,
		repeat=True, repeat_delay=2000)

	plt.show()

