import arcpy #import arcpy tools
from arcpy.sa import * #import spatial analysis tools

arcpy.env.workspace = 'D:/masters_project/strat_model/data/temp_output' #edit to set workspace

arcpy.env.overwriteOutput = True #enable overwriting files

#call clipped climate layers

srad = [] #empty list for solar radiation rasters
meantemp = [] #empty list for mean temperature rasters
mintemp = [] #empty list for minimum temperature rasters
maxtemp = [] #empty list for maximum temperature rasters
x = 1 #set x to number layers by month

#while loop to add the name of each raster input to its respective list
while x < 13:
    srad_name = 'srad'+str(x)+'.tif' #edit to alter srad input names
    meantemp_name = 'meantemp'+str(x)+'.tif' #edit to alter meantemp input names
    mintemp_name = 'mintemp'+str(x)+'.tif' #edit to alter mintemp input names
    maxtemp_name = 'maxtemp'+str(x)+'.tif' #edit to alter maxtemp input names
    srad.append(srad_name) #add to srad
    meantemp.append(meantemp_name) #add to meantemp
    mintemp.append(mintemp_name) #add to mintemp
    maxtemp.append(maxtemp_name) #add to maxtemp
    x += 1 #increase x to keep count

#calculate temperature difference (TD)
i = 0 #set i to track month in list
TD = [] #empty list to collect temperature difference layers

#loop to subtract maxtemp from mintemp for each month, and add the result to TD[]
for month in maxtemp: 
    output = RasterCalculator([month, mintemp[i]], ['x', 'y'], 'x-y') #raster calculation step
    i += 1 #increase i to track month
    save = 'D:/masters_project/strat_model/data/temp_output/TD'+str(i)+'.tif' #edit to alter path/output name
    save2 = 'TD'+str(i)+'.tif' #edit to alter output name
    output.save(save) #save output
    TD.append(save2) #add output name to list

arcpy.env.workspace = 'D:/masters_project/projected_results/data/ssp585/temp_output'

#calculate Potential Evapotranspiration (PET)
i = 0 #set i to track month in list
PET = [] #empty list to collect PET layers

#loop to calculate PET for each month, and add the result to PET[]
for month in srad:
    output = RasterCalculator([month, meantemp[i], TD[i]], ['x', 'y', 'z'],
                              '0.0023*x*(y+17.8)*(z**0.5)') #raster calculation step
    i += 1 #increase i to track month
    save = 'D:/masters_project/strat_model/data/temp_output/PET'+str(i)+'.tif' #edit to alter path/output name
    save2 = 'PET'+str(i)+'.tif' #edit to alter otuput name
    output.save(save) #save output
    PET.append(save2) #add output name to list

#calculate PET average
PETavg = RasterCalculator([PET[0], PET[1], PET[2], PET[3], PET[4], PET[5],
                           PET[6], PET[7], PET[8], PET[9], PET[10], PET[11]], 
                          ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'], 
                         '(a + b + c + d + e + f + g + h + i + j + k + l)/12') #raster calculation step
PETavg.save('D:/masters_project/strat_model/data/temp_output/PETavg.tif') #edit to alter path/output name

#calculate PET seasonality -> standard deviation
i = 0 #set i to track month in list
sqd = [] #empty list to collect the squared distance from the mean for each PET raster

#loop to calculate the square root of the difference between mean PET and each month's PET and add the result to sqd[]
for month in PET:
    sqdist = RasterCalculator([PET[i], 'PETavg.tif'], ['x', 'y'], '(x-y)**2') #raster calculation
    sqd.append(sqdist) #add outputs to sqd list

#calculate standard deviation using sqd values
PETsd = RasterCalculator([sqd[0], sqd[1], sqd[2], sqd[3], sqd[4], sqd[5],
                          sqd[6], sqd[7], sqd[8], sqd[9], sqd[10], sqd[11]], 
                          ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'], 
                         '(((a + b + c + d + e + f + g + h + i + j + k + l)/12)**0.5)*100') #raster calculation
PETsd.save('D:/masters_project/projected_results/data/ssp585/climvar_proj/PETseason.tif') #edit to alter path/output name

#calculate aridity index
AI = RasterCalculator(['meanprecip.tif', 'PETavg.tif'], ['a', 'b'], 'a/b') #raster calculation step
AI.save('D:/masters_project/strat_model/data/climvar/ai.tif') #edit to alter path/output name

#calculate degrees days

#convert values<0 to 0
i = 0 #set i to track month in list
mt = [] #empty list to collect monthly degree days data 

#loop to add the mean temperature of each month to mt[], if the mean temperature <0, add the month's value as 0
for month in meantemp:
    output = RasterCalculator([meantemp[i]], ['x'], 'Con( x<0 ,0 ,x )') #raster calculation step
    i += 1 #increase i to track month
    save = 'D:/masters_project/strat_model/data/temp_output/mt'+str(i)+'.tif' #edit to alter path/output name
    save2 = 'mt'+str(i)+'.tif' #edit to alter output name
    output.save(save) #save output
    mt.append(save2) #add output name to list
    
#add monthly calculations together
degdays = RasterCalculator([mt[0], mt[1], mt[2], mt[3], mt[4], mt[5], mt[6], mt[7], mt[8], mt[9], mt[10], mt[11]], 
                           ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'otc', 'nov', 'dec'], 
                           '(jan*31)+(feb*28.25)+(mar*31)+(apr*30)+(may*31)+(jun*30)+(jul*31)+(aug*31)+(sep*30)+(otc*31)+(nov*30)+(dec*31)') #raster calculation step
degdays.save('D:/masters_project/strat_model/data/climvar/degdays.tif') #edit to alter path/output name

#setup
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.workspace = 'D:/masters_project/maxclass_final/370' #edit to set workspace

arcpy.env.overwriteOutput = True

climvar = ['ai.tif', 'degdays.tif', 'PETseason.tif', 'tseason.tif'] #list the 4 climatic variables

for var in climvar:
    raster = arcpy.Raster(var) #set climatic variable as raster
    rmax = raster.maximum #maximum of the climatic variable
    rmin = raster.minimum #minimum of the climatic variable
    if rmin > 0:
        eq = '(x-'+str(rmin)+')*(100)/('+str(rmax)+'-'+str(rmin)+')' #raster calculation equation for variables without negative values
    else:
        eq = '(x+'+str(rmin).replace('-', '')+')*(100)/('+str(rmax)+'+'+str(rmin).replace('-', '')+')' #raster calculation equation for variables with negative values
    tr = RasterCalculator([var], ['x'], eq) #raster calculation step
    save = 'D:/masters_project/strat_model/data/climvar_transformed/'+str(var) #edit to alter path/output name
    tr.save(save) #save output

# setup
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.workspace = 'E:/masters_project/strat_model/data/climvar_transformed' #edit to set workspace

arcpy.env.overwriteOutput = True

#composite climatic variables into multiple bands of a single raster

arcpy.CompositeBands_management(['tseason_tr.tif','PETseason_tr.tif', 'degdays_tr.tif', 'ai_tr.tif'], 
                                'E:/masters_project/strat_model/data/climvar_tranformed/climvar_composite.tif')

# run isodata algorithm on composited raster

IsoClusterUnsupervisedClassification('climvar_composite.tif', 
                                     'E:/masters_project/strat_model/data/iso_output/isosig.gsg', 
                                     125)
