import pandas as pd
import numpy as np

import requests
import json

from datetime import date
def wu_gethistory(date, stationId='KCOBERTH64', apiKey=None):

  #make the request
  payload = {'stationId': stationId,
           'date':date.strftime('%Y%m%d'),
           'apiKey': apiKey,
           'units': 'm',
           'format': 'json'}
  r = requests.get('https://api.weather.com/v2/pws/history/hourly', params=payload)

  if r.status_code != 200:
    raise ValueError('Invalid request: {0}'.format(r.url))

  #make json doc from the result
  jdoc = r.json()

  if jdoc.get('success') is False:
    raise ValueError('Invalid request; error: {0}'.format(str(jdoc['errors'])))

  # the observation timestamps for later use in indexing
  uts = pd.to_datetime( [obs['obsTimeUtc'] for obs in jdoc['observations']])

  # the temperature data
  df1 = pd.DataFrame([obs['metric'] for obs in jdoc['observations']], index=uts)

  #get the other info
  keylist = [k for k in jdoc['observations'][0].keys() if k != 'metric' ]
  df2 = pd.DataFrame([[obs[k] for k in keylist] for obs in jdoc['observations']], index= uts, columns=keylist)

  #fix up the timestamps
  df2.obsTimeUtc = pd.to_datetime(df2.obsTimeUtc)
  df2.obsTimeLocal = pd.to_datetime(df2.obsTimeLocal)

  #put them together
  wu_data = df2.merge(df1, left_index=True, right_index=True)

  return wu_data

from scipy import interpolate

def get_temps(wu, times):
  t = np.array([t.timestamp() for t in wu.obsTimeUtc])
  w = wu.tempAvg

  t_f = np.array([t.timestamp() for t in times])
  f = interpolate.interp1d(t,w)
  return f(t_f)

from yaml import load
from os.path import expanduser
from datetime import date

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

if __name__ == '__main__':

    with open(expanduser(r'~\Documents\databases.yaml')) as yml:
        credentials = load(yml)

    apiKey = credentials['Wunderground']['apiKey']

    print(f'Api Key: {apiKey}')

    wu_2019_12_20 = wu_gethistory(date(2019,12,20), apiKey=apiKey)
    
    register_matplotlib_converters()
    fmt = mdates.DateFormatter('%H:%M') #formatter to show just the hours and minutes
    fig = plt.figure(figsize=(12,8))
    ax = fig.subplots(nrows=1, ncols=1)

    ax.plot(wu_2019_12_20.index, wu_2019_12_20.tempAvg)
    #ax.plot(dti, get_temps(wu_2019_12_02, dti),'o')
    ax.set_ylabel('Temperature (C)')
    ax.set_xticklabels([fmt(t) for t in ax.get_xticks() ], rotation=90)
    ax.set_xlabel('Time (UT)')
    ax.set_title('Hourly Temperature')

    #ax.plot(dti, get_temps(wu_2019_12_02, dti),'o')
    plt.show()
