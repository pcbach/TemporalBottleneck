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


    
def plotCongection(day,time,city,ax):
    if city == "Melbourne":
        CityShort = 'Mel' #'Bri'
    elif city == "Brisbane":
        CityShort = 'Bri'
    if CityShort == 'Mel':
        bg_color = water_color
        CityFull = 'Melbourne, Australia'
        minLon, minLat, maxLon, maxLat = 144.92271, -37.9380, 145.1777, -37.7715
    elif CityShort == 'Bri':
        bg_color = water_color
        CityFull = 'Queensland, Australia'
        minLon, minLat, maxLon, maxLat = 152.9050, -27.6196, 153.1507, -27.3951
        

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
    q = [{} for _ in range(37)]

    plotHeight = distance.distance((minLat,minLon),(maxLat,minLon)).km
    plotWidth = distance.distance((minLat,minLon),(minLat,maxLon)).km
    with open('./'+city+'/FNets/day_'+str(day)+'.pkl', 'rb') as in_f:
        netdata = pickle.load(in_f)
    for tidx in range(37):
        for l in netdata:
            if netdata[l][tidx] > 0:
                q[tidx][l] = netdata[l][tidx]
    
    sortedBNs = list(q[t2i[time]])#sorted(q[t2i[time]], key=lambda x: q[t2i[time]][x],reverse = True)

    arrow = []
    for e in sortedBNs[:]:
        dist = distance.distance((stopDict[e[0]][1],stopDict[e[0]][0]), (stopDict[e[1]][1],stopDict[e[1]][0])).km
        col = plt.cm.RdYlGn(q[t2i[time]][e])
        LW = (maxLon-minLon)
        cntr = ((stopDict[e[0]][0]+stopDict[e[1]][0])/2,(stopDict[e[0]][1]+stopDict[e[1]][1])/2)
        width = np.sqrt((stopDict[e[0]][0]-stopDict[e[1]][0])**2+(stopDict[e[0]][1]-stopDict[e[1]][1])**2)
        shift = (-(stopDict[e[0]][1]-stopDict[e[1]][1])/width,(stopDict[e[0]][0]-stopDict[e[1]][0])/width)
        height = width/5 if dist>1 else width/100
        angle = np.arctan2((stopDict[e[0]][1]-stopDict[e[1]][1]),(stopDict[e[0]][0]-stopDict[e[1]][0]))* 180 / np.pi
        theta1,theta2 = (0,180) if (angle>0) else (180,360)
        
        scale = 1/3
        if city =="Melbourne":
            cntr = (cntr[0]+shift[0]/5000/scale,cntr[1]+shift[1]/5000/scale)
        else:
            cntr = (cntr[0]+shift[0]/3000/scale,cntr[1]+shift[1]/3000/scale)
        arrow.append(mpatches.Arc(cntr,width,height,angle=angle,theta1 = theta1,theta2 = theta2,color = col,alpha = 1,linewidth = 0.5/scale))
        
                    
            
    collection = PatchCollection(arrow,match_original=True)
    arrow = []
    
    land.plot(ax=ax, zorder=0, fc=land_color)
    ox.plot_footprints(vegetation, ax=ax, bbox=bbox,color=park_color, bgcolor=bg_color,show=False, close=False,alpha = 0.5)
    ox.plot_footprints(water, ax=ax, bbox=bbox,color=water_color, bgcolor=bg_color,show=False, close=False)
    ox.plot_graph(G, ax=ax, node_size=0, bgcolor='white', edge_color='#aaaaaa', edge_linewidth=edgeWidth, edge_alpha=edgeAlpha, show=False, close=False)
    
    ax.add_collection(collection)
    ax.set(xlim=(minLon,maxLon), ylim=(minLat,maxLat))
    ax.set_xticks([])
    ax.set_yticks([])
    
    tt = time if time<13 else (time-12)
    t2h = str(int(np.floor(tt))) + ":" + str(int((tt-np.floor(tt))*60)).zfill(2) + (" AM" if (time<13) else " PM")
    
    #ax.annotate("Day "+str(day)+" "+t2h, xy=(0.02, 0.02), xycoords="axes fraction",fontsize = 8,weight = 'bold') 
    ax.set_title(city+" day "+str(day)+" "+t2h,weight ='bold')
    ax.set_aspect((maxLon-minLon)/(maxLat-minLat)*plotHeight/plotWidth)
    
    ax.set_facecolor(water_color)

nrows = 2
ncols = 3
fig, axs = plt.subplots(nrows=nrows,ncols=ncols)
plotCongection(1,8,"Brisbane",axs[0][0])
plotCongection(2,8,"Melbourne",axs[0][1])
plotCongection(3,8,"Brisbane",axs[0][2])
plotCongection(4,8,"Melbourne",axs[1][0])
plotCongection(5,8,"Melbourne",axs[1][1])
plotCongection(6,8,"Melbourne",axs[1][2])

#plt.subplots_adjust(left= 0,right = 1,bottom=0, top = 1,wspace=0.02, hspace=0.02)
#plt.tight_layout()
#fig.set_size_inches(ncols*3.,nrows*3.*plotHeight/plotWidth)
plt.savefig("./Plot/Congestion.pdf")

plt.show()
