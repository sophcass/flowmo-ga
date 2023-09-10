#! /usr/bin/env python3
import sys, os, fnmatch
from typing import List, Tuple

Genome = List[int]
Population = List[Genome]

#indices of geometric parameters
num_para = 6
length_idx = 0
deflect_idx = 1
pos_out_2_idx = 2
pos_out_1_idx = 3
ratio_out_idx = 4
design_idx = 5


def fitness(genome: Genome, idx: int) -> float:
    if len(genome) != num_para:
        raise ValueError("genome has less than the expected number of parameters")
    
    # create and run a new case file for the geometry
    if genome[design_idx] == 1:
        os.system('cp -r cantileverSecondOutletSS/ testing%d' % idx)
    elif genome[design_idx] == 2:
        os.system('cp -r cantileverSecondOutlet2WithAlterationToBlockMesh/ testing%d' % idx)
    else :
        raise ValueError("genome is neither a strain of design 1 or design 2")

    os.chdir('testing%d' % idx)
    os.system('python modifyMesh.py %0.1f %0.1f %0.1f %0.1f %0.2f > log.modifyMesh' % (genome[length_idx], genome[deflect_idx], genome[pos_out_2_idx], genome[pos_out_1_idx], genome[ratio_out_idx]))
    os.system('blockMesh > log.blockMesh')
    os.system('simpleFoam > log.simpleFoam')
    # os.system('paraFoam -builtin -touch')
    os.system('postProcess -func "flowRatePatch(name=outlet1)" -latestTime > log.flowRateOutlet1')
    os.system('postProcess -func "flowRatePatch(name=outlet2)" -latestTime > log.flowRateOutlet2')
    os.system('postProcess -func "flowRatePatch(name=inlet)" -latestTime > log.flowRateInlet')
    
    # get the flow rate at the primary outlet for an inlet velocity of 2.5m/s
    identifier = "sum(outlet1) of phi"
    f = open('log.flowRateOutlet1', 'r')
    fileLines = f.read()
    fileLines = fileLines.splitlines()
    f.close()
    
    flow_rate1 = 0 # flow_rate1 is the flow rate at the primary outlet for an inlet velocity of 2.5m/s
    for var in enumerate(fileLines):
        if fnmatch.fnmatch(str(var),''.join(['*',identifier,'*'])):
            line = str(var)
            line = line.split()
            flow_rate1 = line[-1] # get the last element in the array
            flow_rate1 = ''.join([n for n in flow_rate1 if n.isdigit() or n == '-' or n == '.' or n == 'e']) # remove any characters that aren't digits from the variable
            flow_rate1 = float(flow_rate1)
    
    # get the flow rate at the secondary outlet for an inlet velocity of 2.5m/s
    identifier = "sum(outlet2) of phi"
    f = open('log.flowRateOutlet2', 'r')
    fileLines = f.read()
    fileLines = fileLines.splitlines()
    f.close()
    
    flow_rate2 = 0 # flow_rate2 is the flow rate at the secondary outlet for an inlet velocity of 2.5m/s
    for var in enumerate(fileLines):
        if fnmatch.fnmatch(str(var),''.join(['*',identifier,'*'])):
            line = str(var)
            line = line.split()
            flow_rate2 = line[-1] # get the last element in the array
            flow_rate2 = ''.join([n for n in flow_rate2 if n.isdigit() or n == '-' or n == '.' or n == 'e']) # remove any characters that aren't digits from the variable
            flow_rate2 = float(flow_rate2)
                    
    # get the flow rate at the inlet for an inlet velocity of 2.5m/s
    identifier = "sum(inlet) of phi"
    f = open('log.flowRateInlet', 'r')
    fileLines = f.read()
    fileLines = fileLines.splitlines()
    f.close()
    
    flow_rate_in = 0 # flow_rate_in is the flow rate at the inlet for an inlet velocity of 2.5m/s
    for var in enumerate(fileLines):
        if fnmatch.fnmatch(str(var),''.join(['*',identifier,'*'])):
            line = str(var)
            line = line.split()
            flow_rate_in = line[-1] # get the last element in the array
            flow_rate_in = ''.join([n for n in flow_rate_in if n.isdigit() or n == '-' or n == '.' or n == 'e']) # remove any characters that aren't digits from the variable
            flow_rate_in = float(flow_rate_in)
    
    os.chdir('..')
    os.system('rm -r testing%d' % idx)

    design_flow_rate = abs(flow_rate_in / design_ratio)
    
    # objective is to minimise the difference between the design flow rate and the flow rate at one of the outlets
    diff_out_1 = abs(flow_rate1 - design_flow_rate)
    diff_out_2 = abs(flow_rate2 - design_flow_rate)
    diff_flow_rate = min(diff_out_1, diff_out_2)
    if flow_rate1 == 0 or flow_rate2 == 0 or diff_flow_rate == 0: # solution is invalid => return a high number so that it is unlikely to be picked for reproduction
        print(f"deviation from the objective flow rate for {genome}: 1000")
        os.system('echo 1000 %d >> log.diffFlowRate' % idx)
        return 1000

    print(f"deviation from the objective flow rate for {genome}: {diff_flow_rate}")
    os.system('echo %0.10f %d  >> log.diffFlowRate' % (diff_flow_rate, idx))
    return diff_flow_rate


# takes in a sting containing the population, index of the relevant genome and the index and returns each of these items separated
def extractGenome(popAndIdx: str) -> Tuple[Genome, int]:
    string = ' '.join([str(elem) for elem in popAndIdx])
    part = string.partition(" ")
    string = part[2] # remove the name of the file
    splitString = string.split(" ") # split the string so that the design ratio and index of the genome can be easily extracted
    
    design_ratio = int(splitString[-1]) # get the index of the design ratio
    idx = int(splitString[-2]) # get the index of the genome in the population

    # get the population
    string = ' '.join(splitString[0:-2])
    string = string[2:-2] # remove brackets from the start and the end of the string
    population = string.split("], [") # create a list of strings for each genome in the population

    pop = []
    for i in range(len(population)):
        genomeString = population[i] # get the string with the first genome
        genomeString = genomeString.split(", ") # create a list of the genes in each genome
        genome = []
        for j in range(len(genomeString)):
            genome.append(float(genomeString[j])) # add each gene to the genome
        pop.append(genome) # add each genome to the population

    return pop[idx], idx, design_ratio # get the relative genome and objective design ratio


argument = sys.argv
genome, idx, design_ratio = extractGenome(argument) # returns the genome, it's corresponding index in the population and the objective design ratio.
fitness(genome, idx)
