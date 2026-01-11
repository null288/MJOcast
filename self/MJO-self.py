# %%
import MJOcast.utils.ProcessForecasts as ProFo 
import MJOcast.utils.ProcessOBS as ProObs
import MJOcast.utils.WHtools as WHtools
import importlib
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import image as mpimg

output_yaml = 'output.yaml'

# %%

MJO_obs = ProObs.MJOobsProcessor(output_yaml)

OBS_DS, eof_list, pcs, MJO_fobs, eof_dict = MJO_obs.make_observed_MJO()

# %%

MJO_for = ProFo.MJOforecaster(output_yaml,MJO_obs.eof_dict,MJO_obs.MJO_fobs)

DS_CESM_for,OLR_cesm_anom_filterd,U200_cesm_anom_filterd,U850_cesm_anom_filterd = MJO_for.create_forecasts(num_files=1)


# %%
