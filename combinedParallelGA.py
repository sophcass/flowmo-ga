#! /usr/bin/env python3
import sys, os, fnmatch, numpy, ast, csv
from functools import partial
from random import choices, uniform, randint, random, randrange 
from typing import List, Callable, Tuple

Genome = List[int]
Population = List[Genome]

SelectionFunc = Callable[[Population], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]

# indices of geometric parameters
num_para = 6
length_idx = 0
deflect_idx = 1
pos_out_2_idx = 2
pos_out_1_idx = 3
ratio_out_idx = 4
design_idx = 5

# ranges of values each geometric parameter can take for design 1
v1length_start = 1.5
v1length_end = 2.6
v1deflect_start = -0.4
v1deflect_end = 0.4
v1pos_out_2_start = 0.2
v1pos_out_2_end = 1.4
v1pos_out_1_start = 1.0
v1pos_out_1_end = 2.5
v1ratio_out_start = 0.25
v1ratio_out_end = 4

# ranges of values each geometric parameter can take for design 2
v2length_start = 1.2
v2length_end = 2.6 
v2deflect_start = -0.4 
v2deflect_end = 0.5
v2pos_out_2_start = 2.7
v2pos_out_2_end = 3.5
v2pos_out_1_start = 0.5
v2pos_out_1_end = 2.5
v2ratio_out_start = 0.25
v2ratio_out_end = 4  


# produces a random number within a range
def random_number_generator(start: float, end: float):
    num = round(uniform(start, end), 2)
    return num


# choose a pair of individuals for reproduction
def selection(population: Population) -> Population:
    prob = numpy.arange(len(population), 0, -1) # weight for the selection process, better performing solutions more likely to be selected
    return choices(
            population = population,
            weights = prob,
            k = 2
    ) 


# cross over function
def crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be the same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]


# mutate a gene with a given probability
def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    if genome[design_idx] != 1 and genome[design_idx] != 2:
        raise ValueError("genome is neither a strain of design 1 or design 2")

    for _ in range(num):
        index = randrange(len(genome))

        if random() > probability:
            genome[index] = genome[index] 
        else: 
            if index == length_idx:
                if genome[design_idx] == 1: 
                    value_length = random_number_generator(v1length_start, v1length_end)
                elif genome[design_idx] == 2:
                    value_length = random_number_generator(v2length_start, v2length_end)
                genome[index] = round(value_length, 1)
            elif index == deflect_idx:
                if genome[design_idx] == 1: 
                    value_deflect = random_number_generator(v1deflect_start, v1deflect_end)
                elif genome[design_idx] == 2: 
                    value_deflect = random_number_generator(v2deflect_start, v2deflect_end)
                genome[index] = round(value_deflect, 1)
            elif index == pos_out_2_idx:
                if genome[design_idx] == 1: 
                    value_out_2 = random_number_generator(v1pos_out_2_start, v1pos_out_2_end)
                elif genome[design_idx] == 2: 
                    value_out_2 = random_number_generator(v2pos_out_2_start, v2pos_out_2_end)
                genome[index] = round(value_out_2, 1)
            elif index == pos_out_1_idx:
                if genome[design_idx] == 1: 
                    value_out_1 = random_number_generator(v1pos_out_1_start, v1pos_out_1_end)
                elif genome[design_idx] == 2: 
                    value_out_1 = random_number_generator(v2pos_out_1_start, v2pos_out_1_end)
                genome[index] = round(value_out_1, 1)
            elif index == ratio_out_idx:
                if genome[design_idx] == 1: 
                    value_ratio_out = (random_number_generator(v1ratio_out_start, v1ratio_out_end))
                elif genome[design_idx] == 2: 
                    value_ratio_out = (random_number_generator(v2ratio_out_start, v2ratio_out_end))
                genome[index] = value_ratio_out
            elif index == design_idx:
                if genome[design_idx] == 1:
                    genome[design_idx] = 2
                elif genome[design_idx] == 2:
                    genome[design_idx] = 1   
    
    if genome[design_idx] == 1: 
        return v1error_handling(genome)
    elif genome[design_idx] == 2:
        return v2error_handling(genome)


# catches combinations of geometric parameters that will cause errors and alters them
def v1error_handling(genome: Genome) -> Genome:
    length = genome[length_idx]
    deflection = genome[deflect_idx]
    out_2_pos = genome[pos_out_2_idx]
    out_1_pos = genome[pos_out_1_idx]
    ratio_out = genome[ratio_out_idx]

    area_out_1 = round((1 / (ratio_out + 1)) * ratio_out, 2)
    area_out_1 = 0.05 * round(area_out_1 / 0.05)
    area_out_2 = round(1 / (ratio_out + 1), 2)
    area_out_2 = 0.05 * round(area_out_2 / 0.05)
    
    if out_2_pos > 2.5: # if the position of outlet 2 is greater than 2.5, this means that the crossover or mutation has flipped the position of outlet 2 from the top to the left hand side. This will bring the geometric parameter for outlet two back to a suitable range.
        out_2_pos = round(random_number_generator(v1pos_out_2_start, v1pos_out_2_end), 1)

    if (out_1_pos + area_out_1) >= 3.0: # error handling, makes sure outlet 1 doesn't exceed the right bounds of the mesh.
        out_1_pos = round(3.0 - (area_out_1 + 0.1), 1)
    
    if out_1_pos >= length: # error handling, makes sure the position of the outlet is at to the left of the end of the cantilever
        out_1_pos = round(length - 0.1, 1)
    
    if out_1_pos <= (out_2_pos + area_out_2 + 0.05): # error handling, makes sure that the outlet 1 and 2 don't overlap
        out_1_pos = round(out_2_pos + area_out_2 + 0.1, 1)
    
    if out_1_pos >= length: # error handling, increases the size of the cantilever if the above conditions has moved the outlet of the primary outlet to the right of the end of the cantilever
        length = round(out_1_pos + area_out_1 + 0.1, 1)
        genome[length_idx] = length

    genome[pos_out_1_idx] = out_1_pos
    genome[pos_out_2_idx] = out_2_pos
    return genome


# catches combinations of geometric parameters that will cause errors and alters them
def v2error_handling(genome: Genome) -> Genome:
    length = genome[length_idx]
    deflection = genome[deflect_idx]
    out_2_pos = genome[pos_out_2_idx]
    out_1_pos = genome[pos_out_1_idx]
    ratio_out = genome[ratio_out_idx]
    
    area_out_1 = round((1 / (ratio_out + 1)) * ratio_out, 2)
    area_out_1 = 0.05 * round(area_out_1 / 0.05)
    area_out_2 = round(1 / (ratio_out + 1), 2)
    area_out_2 = 0.05 * round(area_out_2 / 0.05)
    
    if out_2_pos < 2.5:  # if the position of outlet 2 is less than 2.5, this means that the crossover or mutation has flipped the position of outlet 2 from the left hand side to the top. This will bring the geometric parameter for outlet two back to a suitable range.
        out_2_pos = round(random_number_generator(v2pos_out_2_start, v2pos_out_2_end), 1)

    if (out_1_pos + area_out_1) >= 2.9: # error handling, makes sure outlet 1 doesn't exceed the right bounds of the mesh.
        out_1_pos = round(3.0 - (area_out_1 + 0.1), 1)
    
    if out_1_pos + 0.1 >= length: # error handling, makes sure the position of the outlet is to the left of the end of the cantilever
        out_1_pos = round(length - 0.1, 1)
    
    if (length - (out_1_pos + area_out_1)) > 0.5: # error handling, make sure the end of outlet 1 isn't too far away from the end of the cantilever beam
        out_1_pos = round(length - (area_out_1 + 0.5), 1)
    elif (length - (out_1_pos + area_out_1)) < -0.5:
        diff = (out_1_pos + area_out_1) - length
        diff = diff - 0.5 
        out_1_pos = round(out_1_pos - diff, 1)

    if deflection >= 0.4 and (deflection + 2.5 + 0.2) >= out_2_pos: # error handling, makes sure position of outlet 2 is above the deflection of the beam
        out_2_pos = round(deflection + 2.5 + 0.3, 1)
    elif (deflection + 2.5) >= out_2_pos: 
        out_2_pos = round(deflection + 2.5 + 0.1, 1)
        
    if (out_1_pos + 0.1) >= length:
        out_1_pos = round(length - 0.1, 1)
    
    if (out_2_pos + area_out_2) >= 3.8: # error handling, makes sure outlet 2 doesn't exceed the upper bounds of the mesh
        out_2_pos = round(4.0 - (area_out_2 + 0.2), 1)
        
    if (deflection + 2.5) >= out_2_pos: # error handling, reduce the deflection of the cantilever if the above conditions has moved the secondary outlet below the deflection of the cantilever beam
        deflection = round(out_2_pos - 2.5 - 0.1, 1)
    
    genome[deflect_idx] = deflection
    genome[pos_out_1_idx] = out_1_pos
    genome[pos_out_2_idx] = out_2_pos
    return genome 


# this function defines the run order of an evolution
def run_evolution(population: Population, selection_func: SelectionFunc = selection, crossover_func: CrossoverFunc = crossover, mutation_func: MutationFunc = mutation) -> Population:
    
    diff_flow_rate_file = open("log.diffFlowRate", "r")
    array = diff_flow_rate_file.read().splitlines()
    diff_flow_rate_file.close()
   
    # separate the difference in flow rate and the corresponding indices
    diff_flow_rate = []
    indices = []
    for x in range(0, len(array)):
        chunks = array[x].split(' ')
        diff_flow_rate.append(chunks[0])
        indices.append(chunks[1])

    diff_flow_rate = [diff for _, diff in sorted(zip(indices, diff_flow_rate))] 
    population = [genome for _, genome in sorted(zip(diff_flow_rate, population))] 
    print(f"population in order of fitness: {population}")

    next_generation = population[0:2] # Elitism

    for j in range(int(len(population) / 2) - 1):
        parents = selection_func(population)
        offspring_a, offspring_b = crossover_func(parents[0], parents[1])
        offspring_a = mutation_func(offspring_a)
        offspring_b = mutation_func(offspring_b)
        next_generation += [offspring_a, offspring_b]
        
    population = next_generation
    print(f"next generation: {next_generation}")

    # write next generation to a log file
    next_gen_file = open("log.nextGeneration", "w")
    
    wr = csv.writer(next_gen_file)
    wr.writerows(population)
    return population


def extractGenomes(pop: str) -> Population:

    string = ' '.join([str(elem) for elem in pop])
    part = string.partition(" ")
    string = part[2]
    string = string[2:-2]

    population = string.split("], [")

    pop = []
    for i in range(len(population)):
        genome = population[i]
        genome = genome.split(", ")
        pop.append([float(gene) for gene in genome])

    return pop


argument = sys.argv
pop = extractGenomes(argument)
run_evolution(pop)


