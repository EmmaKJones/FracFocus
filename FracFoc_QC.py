#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas
import matplotlib as plyt
from pandas import ExcelWriter


# In[2]:


#pull in annual frac focus well data (only Texas and only water use >0)
df = pd.read_excel('C:/Users/EJones/Desktop/PYTHON/TX2022.xlsx')


# In[3]:


#clean up table - select only columns needed

df = pd.DataFrame().assign(JobStartDate = df['JobStartDate'], JobEndDate = df['JobEndDate'],APINumber = df['APINumber'].astype("string"), OperatorName = df['OperatorName'], WellName = df['WellName'], Latitude = df['Latitude'], Longitude = df['Longitude'], CountyName = df['CountyName'], Projection = df['Projection'], TotalBaseVolume = df['TotalBaseWaterVolume'])


# In[5]:


#change JobStart Date and JobEndDate fields to correct format and trim API number

df["JobStartDate"]=pd.to_datetime(df["JobStartDate"])
df["JobStartDate"] = df["JobStartDate"].dt.date
df["JobEndDate"]=pd.to_datetime(df["JobEndDate"])
df["JobEndDate"] = df["JobEndDate"].dt.date
df["APINumber"] = df["APINumber"].str[2:10]


# In[7]:


#identify duplicates based on job start and end date, API Number, and water volume used
df["duplicates"] = df.duplicated(subset = ['JobStartDate','JobEndDate', 'APINumber','TotalBaseVolume'], keep=False)


# In[8]:


#select only wells that are duplicates
dups = df[df.duplicates == True]
dups


# In[9]:


#remove duplicate wells
df2 = df.drop_duplicates(subset=['JobStartDate','JobEndDate', 'APINumber','TotalBaseVolume'], keep = 'last')


# In[10]:


#removing boolean column 
df3 = df2.drop(['duplicates'], axis=1)


# In[11]:


#changing TotalBaseVolume to string data type
df3['TotalBaseVolume'] = df3['TotalBaseVolume'].astype(str)


# In[12]:


#seperates wells into tables by their projections
NAD27 = df3[df3.Projection == 'NAD27']
NAD83 = df3[df3.Projection == 'NAD83']
WGS84 = df3[df3.Projection == 'WGS84']
NAD27copy = NAD27.copy()
NAD83copy = NAD83.copy()
WGS84copy = WGS84.copy()


# In[13]:


#brings in county shapefile
county = geopandas.read_file('C:/Users/EJones/Desktop/PYTHON/shp/RCB.shp')


# In[14]:


#creates geometry using lat/long from well records
NAD27copy = geopandas.GeoDataFrame(NAD27copy, geometry = geopandas.points_from_xy(NAD27copy.Longitude, NAD27copy.Latitude), crs="EPSG:4267")
NAD83copy = geopandas.GeoDataFrame(NAD83copy, geometry = geopandas.points_from_xy(NAD83copy.Longitude, NAD83copy.Latitude), crs="EPSG:4269")
WGS84copy = geopandas.GeoDataFrame(WGS84copy, geometry = geopandas.points_from_xy(WGS84copy.Longitude, WGS84copy.Latitude), crs="EPSG:4326")


# In[15]:


#projects county shapeflie in same datum as well records
countyNAD27 = county.to_crs(epsg=4267)
countyNAD83 = county.to_crs(epsg=4269)
countyWGS84 = county.to_crs(epsg=4326)


# In[16]:


#test
NAD27copy.plot()


# In[17]:


#spatial join wells on county
joined = geopandas.sjoin(NAD27copy, countyNAD27, how='left',predicate="within",)
joined2 = geopandas.sjoin(NAD83copy, countyNAD83, how='left',predicate="within",)
joined3 = geopandas.sjoin(WGS84copy, countyWGS84, how='left',predicate="within",)


# In[18]:


#appends all three projection tables backs together
concate = pd.concat([joined.to_crs(epsg=4326),joined2.to_crs(epsg=4326), joined3], axis=0)


# In[19]:


#identifies which wells have mismatch counties
concate['match'] = concate['FIRST_COUN'].str.strip().str.lower()==concate['CountyName'].str.strip().str.lower()
unmatch = concate[concate.match == False]


# In[20]:


#export to excel

with ExcelWriter('C:/Users/EJones/Desktop/PYTHON/Working.xlsx') as writer:
    concate.to_excel(writer, sheet_name = "All_wo_Duplicates")
    dups.to_excel(writer, sheet_name = "Duplicates")
    unmatch.to_excel(writer, sheet_name = "Need_RRC_Review")

