# COVID-19-analysis
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
![GitHub last commit](https://img.shields.io/github/last-commit/ClaudiaRaffaelli/COVID-19-analysis)

## About the project

The aim of this project is to provide some useful insight upon the two datasets provided by the Protezione Civile Italiana organization, reachable at this [link](https://github.com/pcm-dpc/COVID-19). To make best use of the data was also necessary to integrate this two datasets with other [geodata](http://www.diva-gis.org/gdata).

The computations are performed mostly in two files:
- <code>graph_manager.py</code>
- <code>covid-19_pandas_analysis.ipynb</code>

The first file uses the library [NetworkX](https://networkx.github.io/) to build a graph of italian provinces, from the coronavirus data provided. Once the graph has been produced, are performed a few computations. Inside the file, we made available two different versions of the Bellman Ford algorithm. 
The first one, called <code>bellman_ford</code>, is slower and only implements the algorithm with just a few improvements. The other version, called <code>bellman_fordSPFS</code>, implements the variation of the Bellman Ford algorithm called Shortest Path First Algorithm. The main difference between the two algorithms is the presence of a data structure (a deque to be more precise) that speeds up the computation.
It is also made available an implementation of the Betweenness centrality algorithm.

The Jupyter Notebook has the aim of extracting some informations from the data of the two datasets, making a nice visualization of the results obtained. 

Useful links to the Jupyter Notebook:
- [Covid-19 Pandas Analysis](https://nbviewer.jupyter.org/github/ClaudiaRaffaelli/COVID-19-analysis/blob/master/covid-19_pandas_analysis.ipynb)
- [Graph Manager presentation](https://nbviewer.jupyter.org/github/ClaudiaRaffaelli/COVID-19-analysis/blob/master/Graph_manager_presentation.ipynb)

## Repository structure
```
├── covid-19_pandas_analysis.ipynb
├── dati-json
│   ├── dpc-covid19-ita-province.json
│   └── dpc-covid19-ita-regioni.json
├── graph_manager.py
├── Graph_manager_presentation.ipynb
├── Graph_manager_presentation.slides.html
├── LICENSE
├── README.md
└── shape-italy
    ├── ITA_adm0.cpg
    ├── ITA_adm0.csv
    ├── ITA_adm0.dbf
    ├── ITA_adm0.prj
    ├── ITA_adm0.shp
    ├── ITA_adm0.shx
    ├── ITA_adm1.cpg
    ├── ITA_adm1.csv
    ├── ITA_adm1.dbf
    ├── ITA_adm1.prj
    ├── ITA_adm1.shp
    ├── ITA_adm1.shx
    ├── ITA_adm2.cpg
    ├── ITA_adm2.csv
    ├── ITA_adm2.dbf
    ├── ITA_adm2.prj
    ├── ITA_adm2.shp
    ├── ITA_adm2.shx
    ├── ITA_adm3.cpg
    ├── ITA_adm3.csv
    ├── ITA_adm3.dbf
    ├── ITA_adm3.prj
    ├── ITA_adm3.shp
    ├── ITA_adm3.shx
    └── license.txt
```

## Authors
- [Abdullah Chaudhry](https://github.com/chabdullah)
- [Claudia Raffaelli](https://github.com/ClaudiaRaffaelli)

## Acknowledgments
Advanced Algorithms and Graph Mining project - Computer Engineering Master Degree @[University of Florence](https://www.unifi.it/changelang-eng.html)
