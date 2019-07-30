#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:27:47 2019

@author: julian
"""
import os

#https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXAER.5.12.4/2017/12/MERRA2_400.tavg1_2d_aer_Nx.20171226.nc4

año = str(2017)
mes = str(12)

for i in range(18,25):
    dia = str(i)
    os.system('wget --http-user=juliancanellas --http-password=49242964Gollo https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXAER.5.12.4/' 
 + año + '/' + mes + '/' + 'MERRA2_400.tavg1_2d_aer_Nx.'+ año + mes + dia +'.nc4')


import xarray
import glob 

input = glob.glob('wrfinput*')

grid = []

for file in input:
    file = xarray.open_dataset(file)
    grid.append(file)
    
lat = []
lon = []

for dataset in grid:
    auxlat = dataset['XLAT']
    auxlat = auxlat[0,:,0]
    auxlat = auxlat.values
    lat.append(auxlat)
    auxlon = dataset['XLONG']
    auxlon = auxlon[0,0,:]
    auxlon = auxlon.values
    lon.append(auxlon)

import xesmf as xe

nested_grid = []

for i in range(len(lat)):
    auxgrid = {'lon': lon[i], 'lat':lat[i]}
    nested_grid.append(auxgrid)
   
# Ya tengo mis 5 target grids. Ahora tengo que interpolar los datos de aerosol de cada uno de los archivos a CADA UNA DE LAS GRILLAS?!?!?!?!?!?!
    #No, pará, al WRF Solar le tengo que dar 5 archivos y nada más. Lo que debería hacer sería unir todos mis netCDF descargados de MERRA en uno solo y luego hacerle
    # 5 interpolaciones a ese unico archivo.
    
#regridder_bilinear = xe.Regridder(ds, nested_grid, method='bilinear')

##############################################33PAUSAMOS EL INTERPOLADO ##############################################


diciembre2017semana3 = xarray.open_mfdataset('MERRA2_400.tavg1_2d_aer_Nx.201712*')

# Bueno eso fue bastante fácil. Ya tengo todo concatenado. Ahora estoy pensando que debería imitarle los atributos antes de interpolar.     


# No, porque tengo que copiarle los atributos del wrfinput que le corresponde acada dominio. Esto
# en principio no debería hacer falta pero Ruiz Arias dijo que mantengamos los archivos lo más parecidos posible
# a los wrfinput, para evitar que el wrf crashee. Entonces lo que voy a hacer 
# es regriddear primero y convertir a wrfinput despues. Mi producto final tienen que ser 5 archivos con atributos iguales a wrfinput pero con 3 variables, 
#los tres totaer de estos datos MERRA
# Probablemente este producto final no me sirva aún para correr porque voy a tener que hacer esto con la salida del real.exe que use en cada corrida.
# Pero si el script me queda no debería haber mayor problema. 


# Entonces la cosa ahora me quedaría:

ds = diciembre2017semana3

regridder_bilinear = []
for grids in nested_grid:
    auxregridder = xe.Regridder(ds, grids, method='bilinear')
    regridder_bilinear.append(auxregridder)


# bien! Tengo el regridder. Interpolo
    

aerinput_d01 = regridder_bilinear[0](ds)
aerinput_d02 = regridder_bilinear[4](ds)
aerinput_d03 = regridder_bilinear[3](ds)
    
result_list = [] 
varlist = []
for varname, dr in ds.data_vars.items():
    varlist.append(varname)
varlist = [varlist[47],varlist[48],varlist[49]]


for var in varlist:
    ds_temp = regridder_bilinear[0](ds[var])  
    result_list.append(ds_temp) 
aerinput_d01 = xarray.merge(result_list)
result_list = [] 
for var in varlist:
    ds_temp = regridder_bilinear[4](ds[var])  
    result_list.append(ds_temp) 
aerinput_d02 = xarray.merge(result_list)
result_list = [] 
for var in varlist:
    ds_temp = regridder_bilinear[3](ds[var])  
    result_list.append(ds_temp) 
aerinput_d03 = xarray.merge(result_list)
  

aerinput_d01.to_netcdf('aerinput_d01')
aerinput_d02.to_netcdf('aerinput_d02')
aerinput_d03.to_netcdf('aerinput_d03')
###################################SUCCESSSSSSSSSSSSSSSSSSSs#########################################

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from gamap import WhGrYlRd


esperoquesi = regridder_bilinear[0](ds)


fig, axes = plt.subplots(1, 2, figsize=[10, 4], subplot_kw={'projection': ccrs.PlateCarree()})

# Plot global data on the left side
ds.isel(time=0,lat=range(90,130),lon=range(160,200)).plot(ax=axes[0], cmap=WhGrYlRd, 
                                      cbar_kwargs={'shrink': 0.5, 'label': 'mol/mol'})
axes[0].set_title('Conservative regridding')


# Plot nested on on the right side
esperoquesi.isel(time=0).plot(ax=axes[1], cmap=WhGrYlRd, cbar_kwargs={'shrink': 0.5, 'label': 'mol/mol'})

axes[1].set_title('Bilinear regridding')

for ax in axes:
    ax.coastlines()
    ax.gridlines(linestyle='--')

# Para las corridas del solar voy a querer solo 3 dominos, no 5. En realidad podría hacer sólo 3 aerinputs. 



 
## a ver si puedo imitar los wrfinput ahora!
    




















