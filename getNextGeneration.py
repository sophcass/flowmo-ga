#! /usr/bin/env python3
import sys, os
from typing import List
import subprocess

Genome = List[int]
Population = List[Genome]

argument = sys.argv
design_ratio = argument[1]
evolution = argument[2]

#indices of geometric parameters
num_para = 6
length_idx = 0
deflect_idx = 1
pos_out_2_idx = 2
pos_out_1_idx = 3
ratio_out_idx = 4
design_idx = 5

def getNextGenerationFromLogFile() -> Population:
    log_file = open("log.nextGeneration", "r")
    population = log_file.read().splitlines()
    log_file.close()

    pop = []
    for i in range(len(population)):
        genomeString = population[i]
        genomeString = genomeString.split(",")
        genome = []
        for j in range(len(genomeString)):
            genome.append(float(genomeString[j]))
        pop.append(genome)
    
    os.system('echo %s >> log.bestSolutions%s' % (str(pop[0]), design_ratio))

    # Save an image of the best solution from each evolution - this code was added 01/02/22
    # Create and run a new case file for the geometry
    genome = pop[0]
    if genome[design_idx] == 1:
        os.system('cp -r cantileverSecondOutletSS/ testing')
    elif genome[design_idx] == 2:
        os.system('cp -r cantileverSecondOutlet2WithAlterationToBlockMesh/ testing')
    else :
        raise ValueError("genome is neither a strain of design 1 or design 2")

    os.chdir('testing')
    os.system('python modifyMesh.py %0.1f %0.1f %0.1f %0.1f %0.2f > log.modifyMesh' % (genome[length_idx], genome[deflect_idx], genome[pos_out_2_idx], genome[pos_out_1_idx], genome[ratio_out_idx]))
    os.system('blockMesh > log.blockMesh')
    os.system('simpleFoam > log.simpleFoam')
    os.system('paraFoam -builtin -touch >> log.info')

    # Call the saveImg.py script which saves a photo of the evolution, which will be used in the animation
    subprocess.call(['/mnt/c/Program Files/ParaView 5.8.1-Windows-Python3.7-msvc2015-64bit/bin/pvpython.exe', 'saveImg.py'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    os.system('mv evolution.png evolution_%s_%s.png' % (design_ratio, evolution))
    os.system('mv evolution_%s_%s.png ../../flowmo_webapp/flask-server/images/' % (design_ratio, evolution))
    os.chdir('..')
    os.system('rm -r testing')

    return pop


print(getNextGenerationFromLogFile())
