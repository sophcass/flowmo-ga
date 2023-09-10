#!/bin/bash -l
#SBATCH --job-name=GA
#SBATCH -N 1 
#SBATCH --ntasks=10
#SBATCH -t 20:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=sophie.cassidy@ucdconnect.ie

#cd $SLURM_SUBMIT_DIR

#module purge
#module load openfoam/7
#module load python/3.7.4
#source /opt/software/openfoam/7/OpenFOAM-7/etc/bashrc

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/software/gcc/7.4.0/lib64

num_generations=2 # originally set to 200
echo $num_generations
pop_size=2 # population size should be an even number. Orginally set to 10
echo $pop_size 

design_ratio=(10 8 6 5 4 2)
for ratio in "${design_ratio[@]}"
do
    population=$(python3 generateInitialPopCombined.py $pop_size) # get the initial population
    echo $population

    printf -v fname 'log.output%d' "$ratio"
    for ((j=0; j<$num_generations; ++j)); 
    do
        for ((i=0; i<$pop_size; ++i)); 
        do
            echo $i
	        #srun -n1 --exclusive python3 runSimulationCombined.py $population $i $ratio >> $fname & # add onto the file log.output
            python3 runSimulationCombined.py $population $i $ratio >> $fname # add onto the file log.output
        done

        wait

        python3 getAverageAndBestFitness.py $ratio
        
        python3 combinedParallelGA.py $population >> $fname
        nextGeneration=$(python3 getNextGeneration.py $ratio $j)
        population=$nextGeneration
        echo $population
        rm log.diffFlowRate
        rm log.nextGeneration
    done

done

