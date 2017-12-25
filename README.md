# IS452-FinalProject
1.	Project Overview
In the final project, I want to build a Python program which can provide different functionalities for a paper collection such as building the collection automatically add paper, update paper, delete paper and search for paper in the collection as well as extract data out of the collection. 

2.	Module requirement
List of built in modules in PyCharm required for the project: os, csv, re.
import os
import csv
import re
List of modules need to be installed in PyCharm so that the program can be run: matplotlib, networkx.
import networkx as nx
import matplotlib.pyplot as plt

3.	Datasets
The datasets used for the final project contain 8 ASIST conference papers belonging to Library and Information Science Source downloaded from EBSCOhost http://search.ebscohost.com 
Each paper is downloaded both fulltext in pdf format (saved in Datasets/pdf/) and csv file (saved in Datasets/csv/) containing basic information about the paper such as Author, Article Title, Publication Date, ISBN, ISSN,…
The pdf fulltext is then copied into txt file (saved in Datasets/txt/) for processing in the Python program. 
Both txt and csv files should be named similarly; for example, Chong2016.txt and Chong2016.csv.
