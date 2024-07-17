import pickle
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from heapq import *
from itertools import *


def maximum_capacity_paths(graph, source, weight):
    get_weight = lambda u, v, data: data.get(weight, 1)
    #paths = {source: [source]}  # dictionary of paths
    G_succ = graph._adj #G.succ if G.is_directed() else G.adj

    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    pred = {}  # dictionary of final limiting links
    #seen = {source: 0}
    c = count()
    fringe = []
    push(fringe, (-1, source, source))
    while fringe:
        (d, last, v) = pop(fringe)
        dist[v] = d
        for u, e in G_succ[v].items():
            if u == source or u == last:
                continue
            vu_dist = max([dist[v], -get_weight(v, u, e)])
            if u not in dist or vu_dist < dist[u]:
                dist[u] = vu_dist
                push(fringe, (vu_dist, v, u))
                if dist[v] > -get_weight(v, u, e):
                    pred[u] = pred[v]
                else:
                    pred[u] = [(v, u)]
            elif u in dist and vu_dist == dist[u]:
                limit_e = pred[v] if dist[v] > -get_weight(v, u, e) else (v, u)
                if dist[v] > -get_weight(v, u, e):
                    limit_e_list = pred[v]
                elif dist[v] < -get_weight(v, u, e):
                    limit_e_list = [(v, u)]
                else:
                    limit_e_list = pred[v]
                    limit_e_list.append((v, u))
                limit_e_added=False
                for limit_e in limit_e_list:
                    if (limit_e not in pred[u] and (limit_e[1], limit_e[0]) not in pred[u]):
                        limit_e_added = True
                        pred[u].append(limit_e)
                if limit_e_added:
                    push(fringe, (vu_dist, v, u))
    dist = {i: -dist[i] for i in dist}
    return dist, pred


def get_cs(net, od):
    CS = {(edge[0], edge[1]): 0 for edge in net.edges}
    for orig in net:
        _, limitingLinksDict = maximum_capacity_paths(net, orig, weight='q')
        for dest in limitingLinksDict:
            limEdgeCount = float(len(limitingLinksDict[dest]))
            for limEdge in limitingLinksDict[dest]:
                  CS[limEdge] += (od[(orig, dest)]/limEdgeCount if (orig, dest) in od else 0)
    return CS


def calculateDayCS(city,day):
    dayCS = []
    print('Reading day', day)
    with open('./'+city+'/ODs/OD_'+str(day)+'.p', 'rb') as in_f:
        dayOD = pickle.load(in_f)
    with open('./'+city+'/FNets/day_'+str(day)+'.pkl', 'rb') as in_f:
        netdata = pickle.load(in_f)

    print('t_idx:', end='')
    for tidx in range(37):
        netOD = dayOD[tidx]
        G = nx.DiGraph()
        for l in netdata:
            q = netdata[l][tidx]
            if q > 0:
                G.add_edge(l[0], l[1], q=q)
        csDict = {k: v for k, v in get_cs(G, netOD).items() if v != 0}
        dayCS.append(csDict)
        print(tidx, ',', end='')

    print('writing...')
    with open('./'+city+'/Res/CS/CS_day_' + str(day) + '.pkl', 'wb') as out_f:
        pickle.dump(dayCS, out_f)