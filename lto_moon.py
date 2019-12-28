
from  lto_utils.lto_file import LTO_File
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt



def get_weatherdata(spec_chars):
    from yaml import load
    from os.path import expanduser

    with open(expanduser(r'~\Documents\databases.yaml')) as yml:
        credentials = load(yml)

    apiKey = credentials['Wunderground']['apiKey']

    from lto_utils.wunderground import wu_gethistory, get_temps

    #dates (in local time) of the observations
    obs_times = np.concatenate([spec_chars[obs].index for obs in spec_chars])
    min_time = pd.Timestamp(obs_times.min(),tz='UTC').tz_convert('MST7MDT')
    max_time = pd.Timestamp(obs_times.max(),tz='UTC').tz_convert('MST7MDT')
    one_day = pd.Timedelta(days=1)
    obs_days = [ot.to_pydatetime() for ot in pd.date_range(min_time, max_time+one_day,freq='D')]

    weather = pd.concat([wu_gethistory(obs_day,apiKey=apiKey) for obs_day in obs_days])

    return weather

from lto_utils.lto_file import getSpectralCharacteristics
from os import listdir, path

obs_dir=r'e:\moon_obs_2019_12'
obs_list = [f for f in listdir(obs_dir)]

SpecChars = {}
for obs in obs_list:
    SpecChars[obs] = getSpectralCharacteristics(obs_dir + path.sep + obs)

#get the weather data
weather = get_weatherdata(SpecChars)

# put the observation temps on the observations
from lto_utils.wunderground import wu_gethistory, get_temps
for obs in obs_list:
    SpecChars[obs]['ObsTemp'] = get_temps(weather, SpecChars[obs].index)

from datetime import datetime as dt


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import time, timedelta
#get_ipython().run_line_magic('matplotlib', 'inline')

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

fmt = mdates.DateFormatter('%H:%M')

# transits = [
# '2019-10-10 4:24',
# '2019-10-11 5:07',
# '2019-10-12 5:48',
# '2019-10-13 6:30',
# '2019-10-14 7:12'
# #'2019-10-15 7:55'
# #'2019-10-16 8:39'
# ]

# transit_times = [pd.Timestamp(t) for t in transits]

fmt = mdates.DateFormatter('%H:%M')

fig = plt.figure(figsize=(24,12))
axs = fig.subplots(ncols=1, nrows=2, sharex=True)
one_day = timedelta(days=1)

ax = axs[0]
#plot the observations:
for i, obs in enumerate(SpecChars): 
    ax.plot(SpecChars[obs].index-one_day*i, SpecChars[obs].totalpwr, label = obs,
            linewidth= 5)
            #color = obs_colors[i])

ax.set_ylabel('Total Power (Watts)')
#ax.set_ylim(1.35e-17, 1.75e-17)

# for i in range(len(transit_times)):
#     d = transit_times[i]-one_day*i
#     ax.axvline(d, color = obs_colors[i])
#     ax.text(d,1.70e-17,'Transit:\n'+d.strftime('%Y_%m_%d')+'\n'+d.strftime('%X'),
#             ha='center',bbox=dict(facecolor='white', edgecolor=obs_colors[i]))

ax.xaxis.set_major_formatter(fmt)
td = np.array([timedelta(minutes = 15)*m for m in np.arange(17)])
firstdt = SpecChars[list(SpecChars.keys())[0]].index[0]
ax.set_xticks([d for d in firstdt+td])
ax.set_title('Total Power Successive Days')
ax.legend(title='Date:',loc='center left', bbox_to_anchor=(1, 0.5), edgecolor='black')
ax.grid()


#plot temperatures
ax = axs[1]
#plot the observations:
for i, obs in enumerate(SpecChars): 
    ax.plot(SpecChars[obs].index-one_day*i, SpecChars[obs].ObsTemp, label = obs,
            linewidth= 5)
            #color = obs_colors[i])

ax.set_ylabel('Ambient Temperature (C)')

plt.draw()

tl = [fmt(t) for t in ax.get_xticks()]
ax.set_xticklabels(tl, rotation = 90)
ax.set_xlabel('Time (UT)')
ax.set_title('Ambient Temperature 04:30 - 07:30 UT Successive Days\nFull Moon: 2019-10-13')
ax.legend(title='Date:',loc='center left', bbox_to_anchor=(1, 0.5), edgecolor='black')
ax.grid()


plt.show()

    