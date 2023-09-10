#! /usr/bin/env python3
import sys, os, fnmatch, numpy, ast, csv
from functools import partial
from random import choices, uniform, randint, random, randrange 
from typing import List, Callable, Tuple


# this function reads the file holding the differences from the objective flow rate for the current evolution and concatenates the best and average fitness of the evolution into two new log files
def get_average_and_best_fitness(design_ratio: int):
    
    diff_flow_rate_file = open("log.diffFlowRate", "r")
    array = diff_flow_rate_file.read().splitlines()
    diff_flow_rate_file.close()
   
    # separate the difference in flow rate and the corresponding indices
    diff_flow_rate = []
    for x in range(0, len(array)):
        chunks = array[x].split(' ')
        diff_flow_rate.append(float(chunks[0]))

    # get the average fitness and the best fitness of the current evolution
    average_flow_rate = sum(diff_flow_rate) / len(diff_flow_rate)
    os.system('echo %0.10f >> log.averageFitness%s' % (average_flow_rate, design_ratio))
    best_flow_rate = min(diff_flow_rate)
    os.system('echo %0.10f >> log.bestFitness%s' % (best_flow_rate, design_ratio))


argument = sys.argv
design_ratio = argument[1] # get the design ratio, this will be used for naming the files which hold the average and best fitness
get_average_and_best_fitness(design_ratio)


