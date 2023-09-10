import sys, os
from random import uniform
from typing import List

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

# ranges of values each geometric parameter can take for design 1
v1length_start = 1.5
v1length_end = 2.6
v1deflect_start = -0.4
v1deflect_end = 0.4
v1_pos_out_2_start = 0.2
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

# size of population
argument = sys.argv
pop_size = int(argument[1])

# function to create new genomes for design 1                                            
def v1generate_genome(length: int) -> Genome:
    genome = []
    
    for gene in range(length):
        if gene == length_idx:
            value_length = random_number_generator(v1length_start, v1length_end)
            genome.append(round(value_length, 1))
        elif gene == deflect_idx:
            genome.append(round(random_number_generator(v1deflect_start, v1deflect_end), 1))
        elif gene == pos_out_2_idx:
            value_out_2 = random_number_generator(v1_pos_out_2_start, v1pos_out_2_end)
            genome.append(round(value_out_2, 1))
        elif gene == pos_out_1_idx:
            value_out_1 = random_number_generator(v1pos_out_1_start, v1pos_out_1_end)
            genome.append(round(value_out_1, 1))
        elif gene == ratio_out_idx:
            value_ratio_out = (random_number_generator(v1ratio_out_start, v1ratio_out_end))
            genome.append(value_ratio_out)
        elif gene == design_idx:
            value_design = 1 # This genome is a strain of design 1
            genome.append(value_design)

    return v1error_handling(genome) 


# function to create new genomes for design 2
def v2generate_genome(length: int) -> Genome:
    genome = []

    for gene in range(length):
        if gene == length_idx:
            value_length = random_number_generator(v2length_start, v2length_end)
            genome.append(round(value_length, 1))
        elif gene == deflect_idx:
            genome.append(round(random_number_generator(v2deflect_start, v2deflect_end), 1))
        elif gene == pos_out_2_idx:
            value_out_2 = random_number_generator(v2pos_out_2_start, v2pos_out_2_end)
            genome.append(round(value_out_2, 1))
        elif gene == pos_out_1_idx:
            value_out_1 = random_number_generator(v2pos_out_1_start, v2pos_out_1_end)
            genome.append(round(value_out_1, 1))
        elif gene == ratio_out_idx:
            value_ratio_out = (random_number_generator(v2ratio_out_start, v2ratio_out_end))
            genome.append(value_ratio_out)
        elif gene == design_idx:
            value_design = 2 # This genome is a strain of design 2
            genome.append(value_design)
    
    return v2error_handling(genome) 


# function to generate a new population
def generate_population(size: int , genome_length: int) -> Population:
    population = [v1generate_genome(genome_length) for _ in range(size//2)] + [v2generate_genome(genome_length) for _ in range(size//2)] # Half of the initial population is made up of design 1, the other half design 2
    return population


# chooses a randome number within a given range
def random_number_generator(start: float, end:float):
    num = round(uniform(start, end), 2)
    return num


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

print(generate_population(pop_size, num_para))
