import pickle
import networkx as nx

city, version, dayType = 'Melbourne', 'f30w', 'ALL'

t2i = {5+i/2: i for i in range(37)}
WD = [i for i in range(1, 62) if (i%7 != 2 and i%7 != 3 and i != 29)] #62
WE = [i for i in range(1, 62) if i not in WD]

if dayType == 'WD':
    dayList = WD
elif dayType == 'WE':
    dayList = WE
elif dayType == 'ALL':
    dayList = [i for i in range(1, 62)]

for day in dayList:
    dayPC = {}
    print('Reading day', day)
    with open('./'+city+'/ODs/OD120_'+str(day)+'.p', 'rb') as in_f:
        dayOD = pickle.load(in_f)
    with open('./'+city+'/FNets/day_'+str(day)+'_'+version+'.pkl', 'rb') as in_f:
        netdata = pickle.load(in_f)

    for tidx in range(37):
        netOD = dayOD[tidx]
        G = nx.DiGraph()
        for l in netdata:
            q = netdata[l][tidx]
            if q > 0:
                G.add_edge(l[0], l[1], q=q)

        LCC = sorted(nx.strongly_connected_components(G), key=len, reverse=True)[0]
        G.remove_nodes_from([v for v in G if v not in LCC])

        bottlenecks = []
        maxSC = 0
        print(tidx, 'len', len(G), ',', end='')
        for rho_step in range(200+1):
            rho = float(rho_step) / 200
            removed_edges = [(e[0], e[1]) for e in G.edges() if (G[e[0]][e[1]]['q'] <= rho)]
            for e in removed_edges:
                G.remove_edge(e[0], e[1])
            components = sorted(nx.strongly_connected_components(G), key=len, reverse=True)

            if len(components) > 1:
                if len(components[1]) > maxSC:
                    maxSC = len(components[1])
                    #print(removed_edges)
                    bottlenecks = list(removed_edges)
        print(maxSC, len(bottlenecks), ',', end='')
        dayPC[tidx] = list(bottlenecks)
    print('writing...')
    with open('./'+city+'/Res/PC/PC'+str(int(percStepCount))+componentType[0]+'_day_' + str(day) + '_'+version+'.pkl', 'wb') as out_f:
        pickle.dump(dayPC, out_f)
