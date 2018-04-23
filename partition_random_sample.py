from cnf_creator import *
import sys
import os
import math
import random
import pycryptosat
import time
import itertools
import argparse
import subprocess
import numpy as np

###################################
##### RANDOM SAMPLER ##############
###################################

randbool = lambda: random.random() < 0.5

def solverForSample(clauses):
    # set up solver with clauses from original formula
    solver = pycryptosat.Solver()
    for clause in clauses:
        solver.add_clause(clause)
    return solver

def sample_solutions(numMCSamples, counting_vars, clauses): 
    solver = solverForSample(clauses)
    # take samples
    positiveSamples = 0
    for i in range(numMCSamples):
        # generate random assignment to the counting variables
        assumptions = []
        for var in counting_vars.keys():
            if randbool():
                assumptions.append(var)
            else:
                assumptions.append(-var)
        # check if assignment is consistent
        sat, model = solver.solve(assumptions)
        if sat:
            positiveSamples += 1
            for var_assignment in assumptions: 
                if var_assignment > 0:
                    counting_vars[var_assignment] += 1
    return positiveSamples

#############################
##### PARTITIONER ###########
#############################
num_clauses_initial = 0
output = ""
def get_top_vars(k, numMCSamples, filename):
    global num_clauses_initial
    #finds top k partitioning variables of formula after c random samples drawn from the counting variables
    var_counts = np.zeros(k)
    counting_vars = dict()
    #get the number of variables and create the appropriate array
    clauses = []
    with open(filename, 'r') as f:
        for f_line in f:
            line = f_line.split(' ')
            if line[0] == 'c':
                ind_vars = line[2:-1]
                for i in range(len(ind_vars)):
                    counting_vars[int(ind_vars[i])] = 0
            elif line[0] == 'p':
                var_counts = np.zeros(int(line[2]))
            else:
                clauses.append([int(i) for i in line[:-1]])
    counter = sample_solutions(numMCSamples, counting_vars, clauses)
    for i in counting_vars.keys():
        var_counts[i] = counting_vars[i]
    #get k top vars
    for i in range(len(var_counts)):
        if i in counting_vars:
            if var_counts[i] < counter - var_counts[i]:
                var_counts[i] = counter - var_counts[i]
    var_counts = np.argsort(-var_counts)
    return var_counts[:k]

def partition_formula(var_counts, filename):
    n = len(var_counts)
    for index in range(2**n):
        #get binary string corresponding to index
        b = bin(index)[2:]
        l = len(b)
        b = str(0) * (n - l) + b
        ##construct constraint
        assignment = ""
        for i in range(len(b)):
            if b[i] == '1':
                assignment += str(var_counts[i]) + ' 0\n'
            else:
                assignment += '-' + str(var_counts[i]) + ' 0\n'
        #add constraint to original file
        with open(filename.split('.')[0] + ".cnf", 'r') as file:
            data = file.readlines()
        num_data = data[1].split(' ')
        num_data[-1] = str(int(num_data[-1]) + 1) 
        constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
        data[1] = constraints_and_clauses
        ###write modified info back to the file banning this last solution and adjusting the number of clauses
        name = filename.split('.')[0] + '-window-' + str(index) + '.cnf'
        f = open(name, 'w')
        f.writelines(data)
        f.write(assignment)
        f.close()

#################################
##### END PARTITIONER ###########
#################################
if __name__ == "__main__":
    output = str(sys.argv[1]).split('.')[0]
    try:
        k = int(sys.argv[2])
    except:
        k = 4
    with open(output + ".cnf", 'r') as f:
        data = f.readlines()
        with open(output + "copy.cnf", 'w') as filecopy:
            filecopy.writelines(data)
    partition_formula(get_top_vars(k, 5000, output + 'copy.cnf'), output + '.cnf')


