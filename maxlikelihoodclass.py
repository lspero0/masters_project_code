import arcpy #import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.workspace = 'D:/masters_project/maxclass_final/370' #edit to set workspace

arcpy.env.overwriteOutput = True #enable overwriting saved files

# make empty list of inputs
tseason =[] #temperature seasonality
PETseason = [] #PET seasonality 
degdays = [] #degree days
ai = [] #aridity index

i = 0
while i < 13: #for a total of 10 climate models
    i = i+1 #add 1 to i 
    ts = 'norm_bio4_'+str(i)+'.tif' #edit to alter raster names
    pt = 'norm_PETseason'+str(i)+'.tif'
    dd = 'norm_degdays'+str(i)+'.tif' 
    a = 'norm_ai'+str(i)+'.tif'
    tseason.append(ts) #add raster names to list
    PETseason.append(pt)
    degdays.append(dd)
    ai.append(a)

# loop classification, creation out outputs 
mlc = [] #empty list for gathering outputs
sig = 'D:/masters_project/strat_model/isocluster2.gsg' #edit for signature pathway

n=0
for raster in tseason: #MLClassify with 4 bands and signature file
    mlcOut = MLClassify([tseason[n], PETseason[n], degdays[n], ai[n]], sig)
    n = n+1 #increase n
    save = 'D:/masters_project/maxclass_final/370/mlc'+str(n)+'.tif'
    name = 'mlc'+str(n)+'.tif'
    mlcOut.save(save)
    mlc.append(name) #add output mlc list

# assign strata to ecoregions for each model
eco_rast = [ ] # empty list for outputs

for model in mlc:
    polyname = 'poly_'+model.replace('tif', 'shp') #name for output polygon
    arcpy.conversion.RasterToPolygon(model, polyname, 'NO_SIMPLIFY', '#', 'MULTIPLE_OUTER_PART') #raster to polygon
    join_input = polyname[:-4] #alter name for table input to join field
    polyjoin_mean = arcpy.management.JoinField(join_input, 'gridcode', 'eco_relate.csv', 'gridcode', ['eco']) #join field ecoregions
    save = 'out_'+model #name for saving raster output
    arcpy.PolygonToRaster_conversion(polyname, 'eco', save, '#', '#', 'mlc1.tif') #polygon to raster
    eco_rast.append(save) #save final output to join list

print(eco_rast) # check output

#run cell statistic on all mlc outputs
out = CellStatistics([eco_rast[0], eco_rast[1], eco_rast[2], eco_rast[3], eco_rast[4], 
                      eco_rast[5], eco_rast[6], eco_rast[7], eco_rast[8], eco_rast[9], 
                      eco_rast[10], eco_rast[11], eco_rast[12]], "MAJORITY")

#save output
out.save('D:/masters_project/maxclass_final/370/ssp370_maxclass_mode.tif') #edit for maximum likelihood classification output name/path

#setup
import arcpy #import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.workspace = 'D:/masters_project/maxclass_final/370' #edit to set workspace

arcpy.env.overwriteOutput = True #enable overwriting saved files

#call normalized raster names
tseason =[] #temperature seasonality
PETseason = [] #PET seasonality 
degdays = [] #degree days
ai = [] #aridity index

i = 0
while i < 10: #for a total of 10 climate models
    i = i+1 #add 1 to i 
    ts = 'norm_bio4_'+str(i)+'.tif' #edit to alter raster names
    pt = 'norm_PETseason'+str(i)+'.tif'
    dd = 'norm_degdays'+str(i)+'.tif' 
    a = 'norm_ai'+str(i)+'.tif'
    tseason.append(ts) #add raster names to list
    PETseason.append(pt)
    degdays.append(dd)
    ai.append(a)

# average climatic variables
mean_climvar = [] #empty list to gather averaged climatic variables

#tseason
mean_tseason = RasterCalculator([tseason[0], tseason[1], tseason[2], tseason[3], tseason[4],
                                 tseason[5], tseason[6], tseason[7], tseason[8], tseason[9]],
                                ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'], 
                                '(a + b + c + d + e + f + g + h + i + j)/10')
mean_climvar.append(mean_tseason)

#PETseason
mean_PETseason = RasterCalculator([PETseason[0], PETseason[1], PETseason[2], PETseason[3], PETseason[4], 
                                   PETseason[5], PETseason[6], PETseason[7], PETseason[8], PETseason[9]], 
                                  ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'], 
                                  '(a + b + c + d + e + f + g + h + i + j)/10')
mean_climvar.append(mean_PETseason)

#degdays
mean_degdays = RasterCalculator([degdays[0], degdays[1], degdays[2], degdays[3], degdays[4],
                                 degdays[5], degdays[6], degdays[7], degdays[8], degdays[9]],
                                ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'], 
                                '(a + b + c + d + e + f + g + h + i + j)/10')
mean_climvar.append(mean_degdays)

#ai
mean_ai = RasterCalculator([ai[0], ai[1], ai[2], ai[3], ai[4], 
                            ai[5], ai[6], ai[7], ai[8], ai[9]], 
                           ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'], 
                           '(a + b + c + d + e + f + g + h + i + j)/10')
mean_climvar.append(mean_ai)

# run maximum likelihood classification
sig = 'D:/masters_project/strat_model/isocluster2.gsg' #set signature path

mlc_mean = MLClassify([mean_climvar[0], mean_climvar[1], mean_climvar[2], mean_climvar[3]], sig)
save = 'D:/masters_project/maxclass_final/370/mlc_mean.tif'
mlc_mean.save(save)

# convert to polygon
arcpy.conversion.RasterToPolygon('mlc_mean.tif', 'poly_mean.shp', 'NO_SIMPLIFY', '#', 'MULTIPLE_OUTER_PART')

# join field
polyjoin_mean = arcpy.management.JoinField('poly_mean', 'gridcode', 'eco_relate.csv', 'gridcode', ['eco'])

# convert back to raster
save = 'ssp370_maxclass_mean.tif'
arcpy.PolygonToRaster_conversion('poly_mean.shp', 'eco', save, '#', '#', 'mlc_mean.tif')

# conditional statement - if the mode raster's cell value is null, the cell is equal to the mean raster's cell value
mean = 'ssp370_maxclass_mean.tif'
mode = 'ssp370_maxclass_mode.tif'

fill = Con(IsNull(mode), mean, mode)
fill.save('D:/masters_project/maxclass_final/final_rasters/ssp370_class.tif')
