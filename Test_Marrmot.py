#!/usr/bin/env python
# coding: utf-8

# ## Test

# In[133]:


import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import logging
logger_esmvalcore = logging.getLogger('esmvalcore')
logger_esmvalcore.setLevel(logging.WARNING)

import pandas as pd
from cartopy.io import shapereader

import ewatercycle.forcing
import ewatercycle.models
import ewatercycle.analysis
import ewatercycle.observation.grdc


# In[146]:


# Values based on previous calibration
experiment_maximum_soil_moisture_storage = 100.0
experiment_initial_soil_moisture_storage =  0

discharge_variable = "flux_out_Q"
# flux_out_Q unit conversion factor from mm/day to m3/s
conversion_mmday2m3s = 1 / (1000 * 86400)


# In[147]:


forcing = ewatercycle.forcing.generate(
    target_model='marrmot',
    dataset='ERA5',
    start_time='2007-01-01T00:00:00Z',
    end_time='2007-02-27T00:00:00Z',
    shape="/home/vhoogeland/58d28a2d-a141-446a-b8b2-227808c70fd5/data/shapefiles/Missinaibi/Missinaibi_4214531.shp"
)



# print(forcing)


# In[148]:


shape = shapereader.Reader(forcing.shape)
record = next(shape.records())
missinaibi_area = record.attributes["area_hys"] * 1e6
# print("The catchment area is:", missinaibi_area)


# In[152]:


model = ewatercycle.models.MarrmotM01(version='2020.11', forcing=forcing)
# print(model)


# In[154]:


cfg_file, cfg_dir = model.setup(
    # No need to specifiy start and end date, using dates from forcing
    maximum_soil_moisture_storage=experiment_maximum_soil_moisture_storage,
    initial_soil_moisture_storage=experiment_initial_soil_moisture_storage,
)
# print(cfg_file)
# print(cfg_dir)


# In[155]:


model.initialize(cfg_file)


# In[156]:


# obs = ewatercycle.CFG['data/observations/Rhine/6435060_Q_Day.Cmd.txt']

grdc_station_id = '4214531'
observations_df, station_metadata = ewatercycle.observation.grdc.get_grdc_data(
    station_id=grdc_station_id,
    start_time=model.start_time_as_isostr,
    end_time=model.end_time_as_isostr
)


# In[157]:


simulated_discharge = []
timestamps = []

while (model.time < model.end_time):
    model.update()
    timestamps.append(model.time_as_datetime.date())
    # Marrmot M01 is a lumped model, so only single value is returned
    value_in_mmday = model.get_value(discharge_variable)[0]
    # Convert from mm/day to m3/s
    value = value_in_mmday * missinaibi_area * conversion_mmday2m3s
    simulated_discharge.append(value)


# In[158]:


model.finalize()


# In[159]:


simulated_discharge_df = pd.DataFrame(
    {'simulation': simulated_discharge}, index=pd.to_datetime(timestamps)
)
observations_df = observations_df.rename(
    columns={'streamflow': 'observation'}
)
discharge = simulated_discharge_df.join(observations_df)
discharge.to_csv("/home/vhoogeland/58d28a2d-a141-446a-b8b2-227808c70fd5/Research_Skills_Test.csv")


# In[122]:




# ewatercycle.analysis.hydrograph(
#     discharge=discharge,
#     reference='observation',
#     title='Hydrograph Missinaibi 2010'
# )


# In[ ]:





# In[ ]:




