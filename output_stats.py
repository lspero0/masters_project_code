#import modules
import arcpy
from arcpy.ia import *
import pandas as pd
import numpy as np
from osgeo import gdal

arcpy.env.workspace = 'D:/masters_project/analysis/data' #edit to set work

arcpy.env.overwriteOutput = True #enable output overwrite

eco_dict = {'class':[], 'count':[]} #create an empty dictionary
eco = ['historical.tif', 'ssp370_class.tif', 'ssp585_class.tif'] #create a list of present day and predicted scenarios
workspace = 'D:/masters_project/analysis/data' #path as string

for file in eco: #loop for each raster in eco
    path = workspace+'/'+file #path
    raster = gdal.Open(path) #open raster
    band = raster.GetRasterBand(1) #assign band
    cols = raster.RasterXSize #assign columns
    rows = raster.RasterYSize #assign rows
    data = band.ReadAsArray(0, 0, cols, rows).astype(int) #read raster
    uni = np.unique(data,return_counts=True) #find unique values
    eco_dict['class'].append(uni[0]) #add class to dictionary
    eco_dict['count'].append(uni[1]) #add count to dictionary

df_eco = pd.DataFrame(eco_dict) #convert to dataframe
df_eco

#reorganize df and explode lists
df_eco_exp = (pd.DataFrame({c:df_eco[c].explode() for c in eco_dict})
   .set_index('class', append=True)['count'] 
   .unstack(fill_value=0))

#remove NoData column
pixel_count = df_eco_exp.drop(df_eco_exp.columns[0], axis=1)
pixel_count = pixel_count.drop([15], axis=1)

pixel_count.insert(0, 'rowID', ['historical', 'ssp370', 'ssp585']) #add rowID column
pixel_count.to_csv('D:/masters_project/analysis/output_tables/pixel_counts.csv') #save as a .csv
pixel_count #check values look correct

pixel_count2 = pixel_count.drop(['rowID'], axis=1) #no rowid version for future math

pixel_count #check values look correct

#add a new column that sums all the pixels in the row
pixel_count2['pixsum'] = pixel_count2.sum(axis=1)

#create a loop generating new columns for %cover 
i = 0
while i < 8: #loop for columns 1-8
    name = 'class'+str(i+1) #set name for new column, convert to string
    pixel_count2[name] = pixel_count2.iloc[:,i]/pixel_count2.pixsum*100 #append new column calculating %
    i = i+1 #add 1 to i value
    
eco_percent = pixel_count2.drop(pixel_count2.columns[0:9], axis=1) #drop count columns
eco_percent.insert(0, 'rowID', ['historical', 'ssp370', 'ssp585']) #add rowID column

eco_percent.to_csv('D:/masters_project/analysis/output_tables/eco_percent.csv') #save as a .csv
eco_percent #check if it looks right

pixel_count2 = pixel_count2.drop(pixel_count2.columns[8:17], axis=1) #remove % math from previous chunk

#%change math on rows
change_h370 = (pixel_count2.loc[1,:]-pixel_count2.loc[0,:])/pixel_count2.loc[0,:]*100 #%chng between historical and ssp370
change_h585 = (pixel_count2.loc[2,:]-pixel_count2.loc[0,:])/pixel_count2.loc[0,:]*100 #%chng between historical and ssp585
change_370_585 = (pixel_count2.loc[2,:]-pixel_count2.loc[1,:])/pixel_count2.loc[1,:]*100 #%chng between ssp370 and ssp585 

#add outputs to eco_change df
eco_change = pixel_count2.append(change_h370, ignore_index=True) #add h-370 row to eco% as new df eco_change
eco_change = eco_change.append(change_h585, ignore_index=True) #add h-585 row
eco_change = eco_change.append(change_370_585, ignore_index=True) #add 370-585 row

eco_change = eco_change.replace({np.nan:0}) #replace not a number with 0 again
eco_change2 = eco_change.drop([0, 1, 2]) #drop original cell count rows
eco_change2.insert(0, 'rowID', ['chng_h370', 'chng_h585', 'chng_370_585']) #add rowID column
eco_change2.to_csv('D:/masters_project/analysis/output_tables/eco_change.csv') #save as a .csv

eco_change2

#import modules
import arcpy
from arcpy.ia import *
import pandas as pd
import numpy as np
from osgeo import gdal, osr

arcpy.env.workspace = 'D:/masters_project/analysis/data' #edit to change workspace pathing

arcpy.env.overwriteOutput = True #enable overwriting saved outputs

import arcpy
from arcpy import env
from arcpy.sa import * #import system models again

pa = ['KL_PA.shp', 'Barsey_RS.shp', 'Buxa_TR.shp', 'Chapramari_WS.shp', 'Fambong_Lho_WS.shp', 
      'Gorumara_NP.shp', 'Jigme_Khesar_SNR.shp', 'Jore_Pokhari_SS.shp', 'Kanchenjunga_CA.shp',
      'Khangchendzonga_BR.shp', 'Khitam_BS.shp', 'Kyongnosla_AS.shp', 'Mahananda_WS.shp',
     'Mainam_WS.shp', 'Pangolakha_WS.shp', 'Senchal_WS.shp', 'Singhalila_NP.shp', 'Singhba_RS.shp'] #list protected areas
clip = [] #empty list for outputs
n = 1 #set n to track output numbers

#clip historical data
for boundary in pa: #for each protected area
    x = ExtractByMask('historical.tif', boundary) #clip with extract by mask 
    save = 'D:/masters_project/analysis/data/intermediate/'+'hist_'+str(n)+'.tif' #set path for saving
    x.save(save) #save output to path
    name = 'hist_'+str(n)+'.tif' #set name for storage in clip[]
    clip.append(name) #add clip to list
    n += 1 #increase n for next protected area 

#clip ssp370 data
n = 1 #reset n
for boundary in pa: #for each protected area
    x = ExtractByMask('ssp370_class.tif', boundary) #clip
    save = 'D:/masters_project/analysis/data/intermediate/'+'ssp370_'+str(n)+'.tif' #set path for saving
    x.save(save) #save
    name = 'ssp370_'+str(n)+'.tif' #set raster name
    clip.append(name) #add clip to list
    n += 1 #increase n for next protected area 

#clip ssp585 data
n = 1 #reset n
for boundary in pa: #for each protected area
    x = ExtractByMask('ssp585_class.tif', boundary) #clip
    save = 'D:/masters_project/analysis/data/intermediate/'+'ssp585_'+str(n)+'.tif' #set path for saving
    x.save(save) #save
    name = 'ssp585_'+str(n)+'.tif' #set raster name
    clip.append(name) #add clip to list
    n += 1 #increase n for next protected area 
    
print(clip) #check output - should be 18 rasters for each scenarios

workspace = 'D:/masters_project/analysis/data/intermediate' #list workspace as string

pa_dict = {'class':[], 'count':[]} #create an empty dictionary

for file in clip: #list of clipped rasters made earlier
    path = workspace+'/'+file #full path of input raster
    raster = gdal.Open(path) #open raster
    band = raster.GetRasterBand(1) #assign band
    Cols = raster.RasterXSize #assign columns
    Rows = raster.RasterYSize #assign rows
    data = band.ReadAsArray(0, 0, Cols, Rows).astype(int) #read raster
    uni = np.unique(data,return_counts=True) #find unique values
    pa_dict['class'].append(uni[0]) #add class to dictionary
    pa_dict['count'].append(uni[1]) #add count to dictionary

pa_df = pd.DataFrame(pa_dict) #convert to dataframe

pa_df #check output

#generate list for rowID titles
pa = ['All_PA', 'Barsey_RS', 'Buxa_TR', 'Chapramari_WS', 'Fambong_Lho_WS', 
      'Gorumara_NP', 'Jigme_Khesar_SNR', 'Jore_Pokhari_SS', 'Kanchenjunga_CA',
      'Khangchendzonga_BR', 'Khitam_BS', 'Kyongnosla_AS', 'Mahananda',
     'Mainam_WS', 'Pangolakha_WS', 'Senchal_WS', 'Singhalila_NP', 'Singhba_RS'] #list all ecoregion names
raster = ['hist_', 'ssp_370_', 'ssp585_'] #list all scenarios
rowID = [] #empty list to store names

for x in raster: #loop for both scenario and ecoreion list
    for y in pa:
        name = x+y #combine raster and pa name
        rowID.append(name) #add to list

print(rowID) #check output

#reorganize df, explode
pa_df_exp = (pd.DataFrame({c:pa_df[c].explode() for c in pa_df})
   .set_index('class', append=True)['count'] 
   .unstack(fill_value=0))

#remove NoData column
pa_pixel_count = pa_df_exp.drop(pa_df_exp.columns[0], axis=1)
pa_pixel_count = pa_pixel_count.drop([15], axis=1)

pa_pixel_count.insert(0, 'rowID', rowID) #add rowID column
pa_pixel_count.to_csv('D:/masters_project/analysis/output_tables/pa_pixel_counts.csv') #save as a .csv

pa_pixel_count2 = pa_pixel_count.drop(['rowID'], axis=1) #no rowid version for future math

pa_pixel_count #check values look correct

#add a new column that sums all the pixels in the row
pa_pixel_count2['pixsum'] = pa_pixel_count2.sum(axis=1)

#create a loop generating new columns for 
i = 0
while i < 8: #loop for columns 1-8
    name = 'class'+str(i+1) #set name for new column, convert to string
    pa_pixel_count2[name] = pa_pixel_count2.iloc[:,i]/pa_pixel_count2.pixsum*100 #append new column calculating %
    i = i+1 #add 1 to i value
pa_eco_percent = pa_pixel_count2.drop(pa_pixel_count2.columns[0:9], axis=1) #drop count columns

pa_eco_percent.insert(0, 'rowID', rowID) #add rowID column
pa_eco_percent.to_csv('D:/masters_project/analysis/output_tables/pa_eco_percent.csv') #save as a .csv
pa_eco_percent #check if it looks right

count = pd.read_csv('D:/masters_project/analysis/output_tables/pa_pixel_counts.csv') #call pixel count csv from before
count = count.drop(['rowID', 'Unnamed: 0'], axis=1) #drop null rows
count = count.T #transpose table

#generate names for rowIDs
pa = ['All_PA', 'Barsey_RS', 'Buxa_TR', 'Chapramari_WS', 'Fambong_Lho_WS', 
      'Gorumara_NP', 'Jigme_Khesar_SNR', 'Jore_Pokhari_SS', 'Kanchenjunga_CA',
      'Khangchendzonga_BR', 'Khitam_BS', 'Kyongnosla_AS', 'Mahananda',
     'Mainam_WS', 'Pangolakha_WS', 'Senchal_WS', 'Singhalila_NP', 'Singhba_RS'] #protected area names
change = ['h370_', 'h585_', '370_585_'] #%change categories
rowID = [] #empty list for rowid names

for x in change: #loop
    for y in pa:
        name = 'chng_'+x+y #combine each %change category with a pa
        rowID.append(name) #add rowID to list

#calculate %change between historical and ssp370 scenarios
i = 0
while i < 18: #loop for columns 0-17 (hist)
    name = rowID[i] #set column name as rowID
    j = i+18 #ssp370 is 18 rows beyond historical
    count[name] = (count.iloc[:, j]-count.iloc[:, i])/count.iloc[:, i]*100 #append new column calculating %chng
    i = i+1 #add 1 to i value

#calculate %change between historical and ssp585 scenarios
i = 0
while i < 18: #loop for columns 0-17 (hist)
    name = rowID[i+18] #set column name as rowID
    j = i+36 #ssp585 is 36 rows beyond historical
    count[name] = (count.iloc[:, j]-count.iloc[:, i])/count.iloc[:, i]*100 #append new column calculating %chng
    i = i+1 #add 1 to i value

#calculate %change between ssp370 and ssp585 scenarios
while i < 36: #loop for columns 18-35 (ssp370)
    name = rowID[i+18] #set column name as rowID
    j = i+18 #ssp585 is 18 rows beyond ssp370
    count[name] = (count.iloc[:, j]-count.iloc[:, i])/count.iloc[:, i]*100 #append new column calculating %chng
    i = i+1 #add 1 to i value

pa_eco_change = count.drop(count.columns[0:54], axis=1) #drop count columns
pa_eco_change = pa_eco_change.replace({np.nan:0}) #replace NaN from div by 0 errors with 0
pa_eco_change = pa_eco_change.T #transpose dataframe back

pa_eco_change.to_csv('D:/masters_project/analysis/output_tables/pa_eco_change.csv') #save to .csv

pa_eco_change #check outputs
