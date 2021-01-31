# -*- coding: utf-8 -*-
# Derya Gumustel
# Ocean 340
# Final Project

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from collections import OrderedDict
from scipy import stats

def getFileList(path):
    """Takes in a relative path (str), gets list of files in path location, returns lists of file 
    names with and without '.csv'.
    """
    fileList = os.listdir(path)  # get list of files in folder
    fileListOut = []
    locationNames = []
    for dataset in fileList:  # go through every file
        if dataset == "script.py":  # exclude script, want only .csv files
            pass
        else:
            string = str(dataset)  # turn file name into string
            fileListOut.append(dataset)  # add to file list with .csv
            locationNames.append(string[:-4])  # add to file list without .csv
    return fileListOut, locationNames

def openFile(path, fileName):
    """Takes in file path (str) and file name (str), creates pandas dataframe of provided file, 
    returns dataframe.
    """
    df = pd.read_csv(path + fileName)
    return df

def getShallowData(df):
    """Takes in a pandas dataframe, writes new dataframe that contains no rows with depth values 
    greater than 10 ft, returns new dataframe.
    """
    depths = np.arange(10, 100)  # create range of undesired depths
    for depth in depths:  # go through undesired depths
        # write new df from provided df excluding rows that have undesired depths
        discard = " -" + str(depth) + " ft"
        df = df[df[" Depth (Ft)"] != discard]  
    return df
    
def indexByDateTime(df, var):
    """Takes in a pandas dataframe and variable name (str), creates and returns pandas time series
    using the datetime column as an index.
    """
    data = df[var]  # get desired data
    index = pd.DatetimeIndex(df['Date and Time'])  # get desired index (datetime)
    data = pd.Series(list(data), index=index)  # create time series of data
    return data

def avgData(indexedData):
    """Takes in pandas series indexed by datetime, resamples series to get daily averages, returns 
    resampled series.
    """
    series = indexedData
    return series.resample('D').mean()  # resample to daily means

def mergeData(s1, s2):
    """Takes in two pandas series indexed by time, creates dataframes from them, merges the new
    dataframes using the datetime column found in both of them, returns merged dataframe.
    """
    # convert series to dataframes
    df1 = pd.DataFrame({'Date and Time':s1.index, 'Chlorophyll':s1.values})
    df2 = pd.DataFrame({'Date and Time':s2.index, 'Oxygen':s2.values})
    output = pd.merge_asof(df1, df2, on='Date and Time') # merge dataframes using datetime
    return output

def plotAvg(series, figNum, nrows, ncols, index, title, location, ylabel, figsize=[20,10], legend=False):
    """Takes in a pandas series indexed by time, a figure number (int), the number of rows and 
    columns to be used for defining a subplot (ints), the index of that subplot to plot on (int), a 
    plot title (str), a data collection location (str), and a y-label (str). legend=True produces a 
    plot legend. Plots the time series data on desired subplot within figure, shows plot.
    """
    plt.figure(num=figNum, figsize=figsize)  # create figure
    plt.subplot(nrows, ncols, index)  # define subplot system
    plt.subplots_adjust(hspace=0.5)
    
    # add title and axes labels
    plt.title(title, fontsize='xx-large')
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    
    ax = series.plot(style='o', label=location)  # plot series, label by location
    if legend == True:
        ax.legend()  # create legend from series.plot labels
    ax.set_xlim(pd.Timestamp('2019-01-04'), pd.Timestamp('2019-03-08'))  # set x-axis range

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())  # set major ticks to one week intervals
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # set major ticks format
    ax.set_xticklabels([],minor=True)  # show minor ticks
    
    plt.show()

def plotCorr(df, figNum, nrows, ncols, index, title, figsize=[20,10]):
    """Takes in a pandas dataframe containing two variables to be correlated, a figure number (int), 
    the number of rows and columns to be used for defining a subplot (ints), the index of that 
    subplot to plot on (int), and a plot title (str). Plots two variables in the dataframe against 
    each other and calculates and plots the trendline for these two variables. Shows plot and 
    returns r squared value for the two variables.
    """
    plt.figure(num=figNum, figsize=figsize)  # create figure
    plt.subplot(nrows, ncols, index)  # define subplot system
    plt.subplots_adjust(hspace=0.5)
    
    # add title and axes labels
    plt.title(title, fontsize='xx-large')
    plt.xlabel("Chlorophyll (ug/L)")
    plt.ylabel("Oxygen (mg/L)")
    
    # get and plot variable data
    x = df['Chlorophyll']
    y = df['Oxygen']
    plt.plot(x, y, 'o', zorder=2)
    
    # get statistical information
    mask = ~np.isnan(x) & ~np.isnan(y)  # hide nans
    slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], y[mask])
    
    # use stats to plot trendline
    xx = np.array(x)
    yy = slope*xx+intercept
    plt.plot(xx, yy, color='lightsteelblue', ls='-', zorder=1)
    
    plt.show()
    return(r_value**2)  # return r**2 for statistical analysis
    
def plotMap(locationDict, cmap='rainbow', figsize=[10,10]):
    """Takes in an orderered dictionary with data collection sites as keys and corresponding 
    latitude-longitude coordinate pairs as values, creates and shows plot of Puget Sound area with 
    data collection sites plotted appropriately.
    """
    plt.figure(num=4, figsize=figsize)  # create figure
    ax = plt.axes(projection=ccrs.PlateCarree())  # set map projection
    
    # add coastlines and axes ranges
    ax.coastlines(resolution='10m')
    ax.set_extent([-125.5, -122, 46.5, 49.5])
    
    # add colored land and water (ocean feature has long loading time)
    land = cfeature.NaturalEarthFeature('physical', 'land', '10m', facecolor='darkseagreen')
    ax.add_feature(land, zorder=1)
    #ocean = cfeature.NaturalEarthFeature('physical', 'ocean', '10m', facecolor='royalblue')
    #ax.add_feature(ocean, zorder=1)
    
    # add title and gridlines, customize axes labels
    plt.title("Data Collection Sites In and Around Puget Sound", fontsize='xx-large')
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='white', alpha=0.5, linestyle=':', zorder=2)
    gl.xlabels_top = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    
    # plot locations
    colors = eval("plt.cm." + cmap + "(np.linspace(0, 1, len(locationDict)))")
    legendList = list(locationDict.keys())
    for i in range(len(locationDict)):  # for every location
        c = colors[i]  # get new color
        coords = locationDict[legendList[i]]  # get coords from ordered dictionary
        lat = coords[0]
        lon = coords[1]
        plt.scatter(lon, lat, marker='o', color=c, zorder=3, label=legendList[i])  # plot location
        
    ax.legend()  # add legend
    plt.show()


def main():
    script_dir = os.path.dirname(__file__)  # find local script location
    path = script_dir + "\\"  # format to path style 
    fileList, locationNames = getFileList(path)  # use formatted path to access data files
    
    # create and fill ordered location dictionary
    locationDict = OrderedDict()
    locationDict["Bellingham"] = [48.7237, -122.5765]
    locationDict["Coast"] = [47.9627, -124.9580]
    locationDict["Point Williams"] = [47.5372, -122.4061]
    locationDict["Yacht Club, Vashon"] = [47.3942, -122.4635]
    locations = list(locationDict.keys())
    
    rsquaredvals = []
    count = 1
    count3 = 0
    for dataset in fileList:  # go through each file
        
        df = openFile(path, dataset)  # get dataframe 
        place = locationNames[count-1]  # get data collection site 
        
        if ' Chlorophyll' in df.dtypes:  # for every chlorophyll file
            chldf = getShallowData(df)  # get shallow data
            chl = indexByDateTime(chldf, " Chlorophyll")  # get time series
            chlAvg = avgData(chl)  # average series to daily values
            
            # get plots of chlorophyll
            plotAvg(chlAvg, 1, 4, 2, count, place, locations[count3], "Chlorophyll (ug/L)")
            plotAvg(chlAvg, 2, 2, 1, 1, "Chlorophyll Concentrations Across Puget Sound Region", 
            locations[count3], "Chlorophyll (ug/L)", legend=True)
            
        else:  # for every oxygen file
            oxydf = getShallowData(df)  # get shallow data
            oxy = indexByDateTime(oxydf, " Oxygen Conc. (mg/L)")  # get time series
            oxyAvg = avgData(oxy)  # average series to daily values
            
            # get plots of oxygen
            plotAvg(oxyAvg, 1, 4, 2, count, place, locations[count3], "Oxygen (mg/L)")
            plotAvg(oxyAvg, 2, 2, 1, 2, "Oxygen Concentrations Across Puget Sound Region", 
            locations[count3], "Oxygen (mg/L)", legend=True)
            
            # merge chlorophyll and oxygen data, occurs once for each location
            df = mergeData(chlAvg, oxyAvg)
            
            # get r squared values for analysis, get correlation plot
            rsquaredvals.append(plotCorr(df, 3, 2, 2, count3+1, place[:-21]))
            
            count3+=1
        count+=1

    plotMap(locationDict)  # get map of Puget Sound showing data collection sites

if __name__ == "__main__":
    main()