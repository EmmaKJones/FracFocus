#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
import geopandas
import matplotlib as plyt
import numpy as np
from pandas import ExcelWriter


# In[2]:


#pull in well data (after fixing discrepancies with RRC viewer)
df = pd.read_csv('C:/Users/EJones/Desktop/PYTHON/TX_2021.csv')


# In[3]:


#changing TotalBaseVolume to string data type
#df['TBWV_ACFT'] = df['TBWV_ACFT'].astype(str)


# In[4]:


#seperates wells into tables by their projections
NAD27 = df[df.FinalProjection == 'NAD27']
NAD83 = df[df.FinalProjection == 'NAD83']
WGS84 = df[df.FinalProjection == 'WGS84']
NAD27copy = NAD27.copy()
NAD83copy = NAD83.copy()
WGS84copy = WGS84.copy()


# In[5]:


#brings in county shapefile
county = geopandas.read_file('C:/Users/EJones/Desktop/PYTHON/shp/RCB.shp')


# In[6]:


#creates geometry using lat/long from well records
NAD27copy = geopandas.GeoDataFrame(NAD27copy, geometry = geopandas.points_from_xy(NAD27copy.FinalLongitude, NAD27copy.FinalLatitude), crs="EPSG:4267")
NAD83copy = geopandas.GeoDataFrame(NAD83copy, geometry = geopandas.points_from_xy(NAD83copy.FinalLongitude, NAD83copy.FinalLatitude), crs="EPSG:4269")
WGS84copy = geopandas.GeoDataFrame(WGS84copy, geometry = geopandas.points_from_xy(WGS84copy.FinalLongitude, WGS84copy.FinalLatitude), crs="EPSG:4326")


# In[7]:


#projects county shapeflie in same datum as well records
countyNAD27 = county.to_crs(epsg=4267)
countyNAD83 = county.to_crs(epsg=4269)
countyWGS84 = county.to_crs(epsg=4326)


# In[8]:


#spatial join wells on county
joined = geopandas.sjoin(NAD27copy, countyNAD27, how='left',predicate="within",)
joined2 = geopandas.sjoin(NAD83copy, countyNAD83, how='left',predicate="within",)
joined3 = geopandas.sjoin(WGS84copy, countyWGS84, how='left',predicate="within",)


# In[9]:


#appends all three projection tables backs together
concate = pd.concat([joined.to_crs(epsg=4326),joined2.to_crs(epsg=4326), joined3], axis=0)


# In[10]:


#identifies which wells have mismatch counties
concate['match'] = concate['FIRST_COUN'].str.strip().str.lower()==concate['County'].str.strip().str.lower()


# In[11]:


#export to excel
concate.to_csv('C:/Users/EJones/Desktop/PYTHON/concate_v2.csv')


# In[12]:


#counting how many records are still not matching. The code will pause for user input. If there is still records that 
#have lat/long that are not matching lsited county, the user will be able to pause the code and fix the issue then rerun. 
#If all records match, then user should enter 1 then hit "enter".

count = len(concate[concate["match"]!= True])
if count == 0:
    print("Number of records still not matching: ", count)
else: 
    concate.to_csv('C:/Users/EJones/Desktop/PYTHON/concate_v2.csv')
    print("Number of records still not matching: ", count)
user_input = input('Type 1 to continue ')


# In[13]:


#Convert gallons to AcFt

df['TBWV_Acft'] = df['TBWV_Gallons']/325851


# In[14]:


#Bring in Play Splits table

df2 = pd.read_excel('O:/OoP/WSP/PSA/1-Water Uses Estimates-AV/Mining Water Use-AV/FracFocus/1-ReferenceTables/Play_Splits.xlsx', sheet_name=['Play_Splits_2022'])
df2 = df2.get('Play_Splits_2022')
df2['County_Name'] = df2['County_Name'].str.strip().str.upper()


# In[15]:


#Join well table with Play Splits table by County Name

df3=pd.merge(df,df2, left_on='County', right_on='County_Name')
df3.to_csv('C:/Users/EJones/Desktop/PYTHON/merged.csv')
#df3.dtypes


# In[16]:


#seperates wells into tables by their play
Anadarko = df3[df3.Play == 'Anadarko'].copy()
Barnett = df3[df3.Play == 'Barnett'].copy()
Bossier = df3[df3.Play == 'Bossier'].copy()
EagleFord = df3[df3.Play == 'Eagle Ford'].copy()
Haynesville = df3[df3.Play == 'Haynesville'].copy()
Misc = df3[df3.Play == 'Misc'].copy()
Nones1 = df3[df3.Play == 'None'].copy()
Nones2 = df3[df3['Play'].isnull()].copy()
Olmos = df3[df3.Play == 'Olmos'].copy()
Permian = df3[df3.Play == 'Permian'].copy()
PermianFW = df3[df3.Play == 'Permian-Far West'].copy()


# In[17]:


#Merges the wells that either are in the "None" play or are in a county that does not have an identified play
Nones = pd.concat([Nones1, Nones2], ignore_index = True)


# In[18]:


#Will count how many wells are in each play and total amount of wells for QC purposes

print("Anardarko Wells:", len(Anadarko),"\n",
"Barnett Wells:", len(Barnett),"\n",
"Bossier Wells:", len(Bossier),"\n",
"Eagle Ford Wells:", len(EagleFord),"\n",
"Haynesville Wells:", len(Haynesville),"\n",
"Misc Wells:", len(Misc),"\n",
"None Wells:", len(Nones),"\n",
"Olmos Wells:", len(Olmos),"\n",
"Permian Wells:", len(Permian),"\n",
"Permian Far-West Wells:", len(PermianFW))
print("Total wells:", len(Anadarko)+len(Barnett)+len(Bossier)+len(EagleFord)+len(Haynesville)+len(Misc)+len(Nones)+len(Olmos)+len(Permian)+len(PermianFW))


# In[19]:


#Identifies the 1st and 3rd quartiles in the each Play

An = Anadarko['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Ba = Barnett['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Bo = Bossier['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Ef = EagleFord['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Ha = Haynesville['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Mi = Misc['TBWV_ACFT'].quantile(q=[0.75, 0.25])
No = Nones['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Ol = Olmos['TBWV_ACFT'].quantile(q=[0.75, 0.25])
Pe = Permian['TBWV_ACFT'].quantile(q=[0.75, 0.25])
PeW = PermianFW['TBWV_ACFT'].quantile(q=[0.75, 0.25])


# In[20]:


#TooHigh = 2*(float(An.iloc[0])+(1.5*float(An.iloc[0])- float(An.iloc[1])))
#TooLow = (float(An.iloc[1])-(1.5*float(An.iloc[0])- float(An.iloc[1])))/2


# In[21]:


#Identifies the outliers

Anoutliers = Anadarko.loc[(Anadarko['TBWV_ACFT'] > 2*(float(An.iloc[0])+(1.5*float(An.iloc[0])- float(An.iloc[1])))) | (Anadarko['TBWV_ACFT'] < (float(An.iloc[1])-(1.5*float(An.iloc[0])- float(An.iloc[1])))/2)]
Baoutliers = Barnett.loc[(Barnett['TBWV_ACFT'] > 2*(float(Ba.iloc[0])+(1.5*float(Ba.iloc[0])- float(Ba.iloc[1])))) | (Barnett['TBWV_ACFT'] < (float(Ba.iloc[1])-(1.5*float(Ba.iloc[0])- float(Ba.iloc[1])))/2)]
Booutliers = Bossier.loc[(Bossier['TBWV_ACFT'] > 2*(float(Bo.iloc[0])+(1.5*float(Bo.iloc[0])- float(Bo.iloc[1])))) | (Bossier['TBWV_ACFT'] < (float(Bo.iloc[1])-(1.5*float(Bo.iloc[0])- float(Bo.iloc[1])))/2)]
Efoutliers = EagleFord.loc[(EagleFord['TBWV_ACFT'] > 2*(float(Ef.iloc[0])+(1.5*float(Ef.iloc[0])- float(Ef.iloc[1])))) | (EagleFord['TBWV_ACFT'] < (float(Ef.iloc[1])-(1.5*float(Ef.iloc[0])- float(Ef.iloc[1])))/2)]
Haoutliers = Haynesville.loc[(Haynesville['TBWV_ACFT'] > 2*(float(Ha.iloc[0])+(1.5*float(Ha.iloc[0])- float(Ha.iloc[1])))) | (Haynesville['TBWV_ACFT'] < (float(Ha.iloc[1])-(1.5*float(Ha.iloc[0])- float(Ha.iloc[1])))/2)]
Mioutliers = Misc.loc[(Misc['TBWV_ACFT'] > 2*(float(Mi.iloc[0])+(1.5*float(Mi.iloc[0])- float(Mi.iloc[1])))) | (Misc['TBWV_ACFT'] < (float(Mi.iloc[1])-(1.5*float(Mi.iloc[0])- float(Mi.iloc[1])))/2)]
Nooutliers = Nones.loc[(Nones['TBWV_ACFT'] > 2*(float(No.iloc[0])+(1.5*float(No.iloc[0])- float(No.iloc[1])))) | (Nones['TBWV_ACFT'] < (float(No.iloc[1])-(1.5*float(No.iloc[0])- float(No.iloc[1])))/2)]
Oloutliers = Olmos.loc[(Olmos['TBWV_ACFT'] > 2*(float(Ol.iloc[0])+(1.5*float(Ol.iloc[0])- float(Ol.iloc[1])))) | (Olmos['TBWV_ACFT'] < (float(Ol.iloc[1])-(1.5*float(Ol.iloc[0])- float(Ol.iloc[1])))/2)]
Peoutliers = Permian.loc[(Permian['TBWV_ACFT'] > 2*(float(Pe.iloc[0])+(1.5*float(Pe.iloc[0])- float(Pe.iloc[1])))) | (Permian['TBWV_ACFT'] < (float(Pe.iloc[1])-(1.5*float(Pe.iloc[0])- float(Pe.iloc[1])))/2)]
PeWoutliers = PermianFW.loc[(PermianFW['TBWV_ACFT'] > 2*(float(PeW.iloc[0])+(1.5*float(PeW.iloc[0])- float(PeW.iloc[1])))) | (PermianFW['TBWV_ACFT'] < (float(PeW.iloc[1])-(1.5*float(PeW.iloc[0])- float(PeW.iloc[1])))/2)]


# In[22]:


#merge all the outliers into one dataframe

concate = pd.concat([Anoutliers, Baoutliers, Booutliers, Efoutliers, Haoutliers, Mioutliers, Nooutliers, Oloutliers, Peoutliers, PeWoutliers], axis=0)


# In[23]:


#remove outliers from whole dataset

df3 = df3.drop(concate.index)


# In[24]:


#calculate the mean and standard deviation of the water use for each well

mean = df3["TBWV_ACFT"].mean()
stde = df3["TBWV_ACFT"].std()


# In[25]:


#Calculate the z-scores and find and well that has a z-score over 5
zscores = df3.loc[((df3['TBWV_ACFT']-mean)/stde) > 5]


# In[27]:


#Drop the wells with z-score over 5 out of total dataset

df3 = df3.drop(zscores.index)


# In[37]:


#Exports the outliers, wells with z score over 5, and final well dataset to excel

with ExcelWriter('C:/Users/EJones/Desktop/PYTHON/FINAL.xlsx') as writer:
    concate.to_excel(writer, sheet_name = "Outlier")
    zscores.to_excel(writer, sheet_name = "Z-Scores")
    df3.to_excel(writer, sheet_name = "FINAL")

