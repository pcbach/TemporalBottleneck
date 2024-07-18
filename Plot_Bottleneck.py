import pickle
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from heapq import *
from itertools import *
from geopy import distance
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import osmnx as ox
import pickle
import matplotlib.pyplot as plt
import os.path

subfontsize = 10
    
water_color = '#9ED2EA' #'#9ED2EA' #'#ccccff'
land_color = '#FFF9EC'#'#f6f0e4' #'#ffffff'
park_color = '#cee1af'
Redish_color = "#ff573c"
Bluish_color = "#30649e"
Greenish_color = '#cf7ac3'



def read_stop_clusters(stop_clusters_data,city):
    clusters_com = {}
    stop2cluster = {}
    with open(stop_clusters_data, 'r') as in_f:
        for line in in_f:
            linesplit = [float(i.strip()) for i in line.split(',')]
            if city == "Melbourne":
                sid = int(linesplit[0])
                cid = int(linesplit[3])
                com_coord = (linesplit[5], linesplit[4])
            elif city == "Brisbane":
                sid = int(linesplit[0])
                cid = int(linesplit[5])
                com_coord = (linesplit[7], linesplit[6])
                
            if sid not in stop2cluster:
                stop2cluster[sid] = cid
            if cid not in clusters_com:
                clusters_com[cid] = com_coord
    return stop2cluster, clusters_com


    
def plotFABottleneck(day,time,city,topCnt,ax):
    if city == "Melbourne":
        CityShort = 'Mel'
    elif city == "Brisbane":
        CityShort = 'Bri'
    if CityShort == 'Mel':
        bg_color = water_color
        CityFull = 'Melbourne, Australia'
        minLon, minLat, maxLon, maxLat = 144.855, -37.95686, 145.12902, -37.74031
    elif CityShort == 'Bri':
        bg_color = water_color
        CityFull = 'Queensland, Australia'
        minLon, minLat, maxLon, maxLat = 152.9070, -27.6118, 153.1507, -27.3951
        
    #query map data
    bbox = maxLat, minLat, maxLon, minLon
    if not os.path.isfile('./MapData/'+CityShort+'DriveNet.pkl'):
        G = ox.graph_from_bbox(minLat, maxLat, minLon, maxLon, network_type='drive', simplify=True)
        pickle.dump(G, open('./MapData/'+CityShort+'DriveNet.pkl', 'wb'))
    else:
        G = pickle.load(open('./MapData/'+CityShort+'DriveNet.pkl', 'rb'))


    ox.config(log_console=True, use_cache=True)

    if not os.path.isfile('./MapData/'+CityShort+'LandWater.pkl'):
        land = ox.geocode_to_gdf(CityFull)
        poly = ox.utils_geo.bbox_to_poly(*bbox)
        water = ox.geometries_from_polygon(poly, tags={'natural': 'water'})
        vegetation = ox.geometries_from_polygon(poly, tags={'leisure': 'park'})
        with open('./MapData/'+CityShort+'LandWater.pkl', 'wb') as in_file:
            pickle.dump([land, water, vegetation], in_file)
    else:
        with open('./MapData/' + CityShort + 'LandWater.pkl', 'rb') as out_file:
            land, water, vegetation = pickle.load(out_file)


    eTypeList = []
    deleteList = []
    for uu, vv, kkey, ddata in G.edges(keys=True, data=True):
        eHighway = ddata['highway'][0] if type(ddata['highway'])==list else ddata['highway']
        if eHighway in ['road', 'crossing', 'unclassified', 'disused', 'residential', 'residential_link', 'living_street',
                        'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'teritary_link']:
            deleteList.append((uu, vv))
        else:
            eTypeList.append(eHighway)

    for edgeTuple in deleteList:
        G.remove_edge(edgeTuple[0], edgeTuple[1])
        
    edgeVizDict = {
                'motorway': (1, .8),
                'trunk': (0.66, .8),
                'primary': (0.66, .5),
                'secondary': (0.66, .2),
                'tertiary': (.33, .2),
                'busway': (0.66, 0.5)
                }
        
    edgeWidth = [edgeVizDict[etype][0] for etype in eTypeList]
    edgeAlpha = [edgeVizDict[etype][1]*5/4 for etype in eTypeList]
    stopClusterData = './MapData/MelNodeCoord.csv' if (city=="Melbourne") else './MapData/BriNodeCoord.csv'
    _, stopDict = read_stop_clusters(stopClusterData,city)
    
    t2i = {5+i/2: i for i in range(37)}
    
    plotHeight = distance.distance((minLat,minLon),(maxLat,minLon)).km
    plotWidth = distance.distance((minLat,minLon),(minLat,maxLon)).km
    hourCS = [{} for _ in range(37)]
    
    #read criticality score
    with open('./'+city+'/Res/CS/CS_day_' + str(day) + '.pkl', 'rb') as in_f:
        dayCS = pickle.load(in_f)

    for tidx in range(37):
        totalFlux = np.sum([dayCS[tidx][l] for l in dayCS[tidx]])
        for l in dayCS[tidx]:
            if l not in hourCS[tidx]:
                hourCS[tidx][l] = 0
            hourCS[tidx][l] += dayCS[tidx][l]/totalFlux

    
    sortedBNs = sorted(hourCS[t2i[time]], key=lambda x: hourCS[t2i[time]][x], reverse=True)
        
    

    arrow = []
    cnt = 0
    for e in sortedBNs[:]:
        if cnt<topCnt:
            cnt = cnt+1
            dist = distance.distance((stopDict[e[0]][1],stopDict[e[0]][0]), (stopDict[e[1]][1],stopDict[e[1]][0])).km
            if dist > 7:
                continue
            col = Redish_color
            
            LW = 1/40
            scale = 1
            scale = (scale-1)/2
            style="Simple,head_length="+str(0.1*LW*dist)+",head_width="+str(0.3*LW)+",tail_width="+str(0.1*LW)
            dir = (stopDict[e[1]][0]-stopDict[e[0]][0],stopDict[e[1]][1]-stopDict[e[0]][1])
            arrow.append(mpatches.FancyArrowPatch(  (stopDict[e[0]][0]-scale*dir[0], stopDict[e[0]][1]-scale*dir[1]),
                                                    (stopDict[e[1]][0]+scale*dir[0], stopDict[e[1]][1]+scale*dir[1]),
                                                    facecolor = col,edgecolor = 'none',alpha = 1,linewidth = 0.1,
                                                    arrowstyle=style,  shrinkA=0,  shrinkB=0,connectionstyle="arc3,rad=0.001"))
            
                                
                
    collection = PatchCollection(arrow,match_original=True, zorder=2)
    arrow = []
    land.plot(ax=ax, zorder=0, fc=land_color)
    ox.plot_footprints(vegetation, ax=ax, bbox=bbox,color=park_color, bgcolor=bg_color,show=False, close=False)
    ox.plot_footprints(water, ax=ax, bbox=bbox,color=water_color, bgcolor=bg_color,show=False, close=False)
    ox.plot_graph(G, ax=ax, node_size=0, bgcolor='white', edge_color='#aaaaaa', edge_linewidth=edgeWidth, edge_alpha=edgeAlpha, show=False, close=False)
    ax.add_patch(mpatches.Rectangle((minLon,minLat),maxLon-minLon,maxLat-minLat,lw = 1,facecolor = 'none',edgecolor = 'black', zorder=3))
    
    ax.add_collection(collection)
        
    ax.set(xlim=(minLon,maxLon), ylim=(minLat,maxLat))
    ax.set_xticks([])
    ax.set_yticks([])

    tt = time if time<13 else (time-12)
    t2h = str(int(np.floor(tt))) + ":" + str(int((tt-np.floor(tt))*60)).zfill(2) + (" AM" if (time<13) else " PM")

    ax.set_title(city+" day "+str(day)+" "+t2h,weight ='bold',fontsize = subfontsize)
    ax.set_aspect((maxLon-minLon)/(maxLat-minLat)*plotHeight/plotWidth)

    ax.set_facecolor(water_color)

   
def plotPTBottleneck(day,time,city,ax):
    if city == "Melbourne":
        CityShort = 'Mel'
    elif city == "Brisbane":
        CityShort = 'Bri'
    if CityShort == 'Mel':
        bg_color = water_color
        CityFull = 'Melbourne, Australia'
        minLon, minLat, maxLon, maxLat = 144.855, -37.95686, 145.12902, -37.74031
    elif CityShort == 'Bri':
        bg_color = water_color
        CityFull = 'Queensland, Australia'
        minLon, minLat, maxLon, maxLat = 152.9070, -27.6118, 153.1507, -27.3951
        

    #query map data
    bbox = maxLat, minLat, maxLon, minLon
    if not os.path.isfile('./MapData/'+CityShort+'DriveNet.pkl'):
        G = ox.graph_from_bbox(minLat, maxLat, minLon, maxLon, network_type='drive', simplify=True)
        pickle.dump(G, open('./MapData/'+CityShort+'DriveNet.pkl', 'wb'))
    else:
        G = pickle.load(open('./MapData/'+CityShort+'DriveNet.pkl', 'rb'))


    ox.config(log_console=True, use_cache=True)

    if not os.path.isfile('./MapData/'+CityShort+'LandWater.pkl'):
        land = ox.geocode_to_gdf(CityFull)
        poly = ox.utils_geo.bbox_to_poly(*bbox)
        water = ox.geometries_from_polygon(poly, tags={'natural': 'water'})
        vegetation = ox.geometries_from_polygon(poly, tags={'leisure': 'park'})
        with open('./MapData/'+CityShort+'LandWater.pkl', 'wb') as in_file:
            pickle.dump([land, water, vegetation], in_file)
    else:
        with open('./MapData/' + CityShort + 'LandWater.pkl', 'rb') as out_file:
            land, water, vegetation = pickle.load(out_file)


    eTypeList = []
    deleteList = []
    for uu, vv, kkey, ddata in G.edges(keys=True, data=True):
        eHighway = ddata['highway'][0] if type(ddata['highway'])==list else ddata['highway']
        if eHighway in ['road', 'crossing', 'unclassified', 'disused', 'residential', 'residential_link', 'living_street',
                        'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'teritary_link']:
            deleteList.append((uu, vv))
        else:
            eTypeList.append(eHighway)

    for edgeTuple in deleteList:
        G.remove_edge(edgeTuple[0], edgeTuple[1])
        
    edgeVizDict = {
                'motorway': (1, .8),
                'trunk': (0.66, .8),
                'primary': (0.66, .5),
                'secondary': (0.66, .2),
                'tertiary': (.33, .2),
                'busway': (0.66, 0.5)
                }
        
    edgeWidth = [edgeVizDict[etype][0] for etype in eTypeList]
    edgeAlpha = [edgeVizDict[etype][1]*5/4 for etype in eTypeList]
    stopClusterData = './MapData/MelNodeCoord.csv' if (city=="Melbourne") else './MapData/BriNodeCoord.csv'
    _, stopDict = read_stop_clusters(stopClusterData,city)
    
    t2i = {5+i/2: i for i in range(37)}
    
    plotHeight = distance.distance((minLat,minLon),(maxLat,minLon)).km
    plotWidth = distance.distance((minLat,minLon),(minLat,maxLon)).km
    
    #read PT Bottlenecks
    with open('./'+city+'/Res/PT/PT_day_' + str(day) + '.pkl', 'rb') as in_f:
        dayPT = pickle.load(in_f)


    BNs = list(dayPT[t2i[time]])
    arrow = []
    cnt = 0
    for e in BNs:
        cnt = cnt+1
        dist = distance.distance((stopDict[e[0]][1],stopDict[e[0]][0]), (stopDict[e[1]][1],stopDict[e[1]][0])).km
        if dist > 7:
            continue
        col = Bluish_color
        
        LW = 1/40
        scale = 1
        scale = (scale-1)/2
        style="Simple,head_length="+str(0.2*LW*dist)+",head_width="+str(0.3*LW)+",tail_width="+str(0.1*LW)
        dir = (stopDict[e[1]][0]-stopDict[e[0]][0],stopDict[e[1]][1]-stopDict[e[0]][1])
        arrow.append(mpatches.FancyArrowPatch(  (stopDict[e[0]][0]-scale*dir[0], stopDict[e[0]][1]-scale*dir[1]),
                                                (stopDict[e[1]][0]+scale*dir[0], stopDict[e[1]][1]+scale*dir[1]),
                                                facecolor = col,edgecolor = 'none',alpha = 1,linewidth = 0.1,
                                                arrowstyle=style,  shrinkA=0,  shrinkB=0,connectionstyle="arc3,rad=0.001"))
            
                                
                
    collection = PatchCollection(arrow,match_original=True, zorder=2)
    arrow = []
    land.plot(ax=ax, zorder=0, fc=land_color)
    ox.plot_footprints(vegetation, ax=ax, bbox=bbox,color=park_color, bgcolor=bg_color,show=False, close=False)
    ox.plot_footprints(water, ax=ax, bbox=bbox,color=water_color, bgcolor=bg_color,show=False, close=False)
    ox.plot_graph(G, ax=ax, node_size=0, bgcolor='white', edge_color='#aaaaaa', edge_linewidth=edgeWidth, edge_alpha=edgeAlpha, show=False, close=False)
    ax.add_patch(mpatches.Rectangle((minLon,minLat),maxLon-minLon,maxLat-minLat,lw = 1,facecolor = 'none',edgecolor = 'black', zorder=3))
    
    ax.add_collection(collection)
        
    ax.set(xlim=(minLon,maxLon), ylim=(minLat,maxLat))
    ax.set_xticks([])
    ax.set_yticks([])

    tt = time if time<13 else (time-12)
    t2h = str(int(np.floor(tt))) + ":" + str(int((tt-np.floor(tt))*60)).zfill(2) + (" AM" if (time<13) else " PM")

    ax.set_title(city+" day "+str(day)+" "+t2h,weight ='bold',fontsize = subfontsize)
    ax.set_aspect((maxLon-minLon)/(maxLat-minLat)*plotHeight/plotWidth)

    ax.set_facecolor(water_color)
        
nrows = 1
ncols = 2
fig, axs = plt.subplots(nrows=nrows,ncols=ncols)
plotPTBottleneck(1,8.5,"Melbourne",axs[0])
plotPTBottleneck(1,8.5,"Brisbane",axs[1])
plotFABottleneck(1,8.5,"Melbourne",8,axs[0])
plotFABottleneck(1,8.5,"Brisbane",8,axs[1])
fig.set_size_inches(4.*ncols,4.*nrows)
plt.savefig("./Plot/Bottlenecks.pdf")