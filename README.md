# Supplementary Codes for: Temporal patterns in percolation bottlenecks of congested city transport networks
## Code author: H.H and C.P

This is a Python package created for our paper titled: _"Temporal patterns in percolation bottlenecks of congested city transport networks"_, submitted for publication in Nature Cities.
This repository contains 15 consecutive days of public transport data for Melbourne and Brisbane(organized into two folders with respective name), which consisted of network and origin-destination info.


### Getting the code
Download all the files in this repository by cloning the repository:
```
git clone https://github.com/pcbach/TemporalBottleneck.git
```

### Code usage
#### Calculate criticality score
To find the limiting links and calculate the CS score of all links on a specific day, from _Calculate_CS_Score.py_ run 
```
calculateDayCS(city,day)
```

#### Find phase transition bottlenecks
To find the list of phase transition bottlenecks on a specific day, from _Find_PT_Bottleneck.py_ run 
```
calculateDayPTB(city,day)
```

#### Plot map of link speed
To plot the congestion map like those in the top panels of Fig.1B in the main text, from _Plot_Congestion_Map.py_ run 
```
plotCongestion(day,time,city,axs)
```
Here, ```axs``` is a matplotlib.axes object

#### Plot map of bottlenecks
To plot the map of bottlenecks like those in the top panels of Fig.1C in the main text, from _Plot_Bottleneck.py_, for phase transition bottlenecks, run
```
plotPTBottleneck(day,time,city,axs)
```
For flux-aware bottlenecks, run
```
plotFABottleneck(day,time,city,num,axs)
```
Here, ```axs``` is a matplotlib.axes object and ``` num ``` is the number of bottleneck to plot (selected with the highest CS score). 
