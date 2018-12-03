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

def random_string_generator(k):
    assignment_str = ""
    for i in range(k):
        if randbool():
            assignment_str += "1"
        else:
            assignment_str += "0"
    return assignment_str

def solverForSample(clauses):
    # set up solver with clauses from original formula
    solver = pycryptosat.Solver()
    for clause in clauses:
        solver.add_clause(clause)
    return solver

def sample_solutions(numSamples, counting_vars, clauses): 
    solver = solverForSample(clauses)
    # take samples
    positiveSamples = 0
    loss_vector = np.zeros(max(counting_vars.keys()) + 1)
    loss_vector_neg = np.zeros(max(counting_vars.keys()) + 1)
    counting_vars_pos = counting_vars.copy()
    counting_vars_neg = counting_vars.copy()

    assignments = set()
    for T in range(min(2**len(counting_vars.keys()), numSamples)):
        # generate random assignment to the counting variables
        assumptions = []
        counting_vars_iteration_value = dict()
        assignment_str = ""
        while assignment_str == "" or assignment_str in assignments:
            assignment_str = ""
            for var in counting_vars.keys():
                if randbool() > 0.5:
                    assumptions.append(var)
                    assignment_str += " " + str(var)
                    counting_vars_iteration_value[var] = 1
                else:
                    assumptions.append(-var)
                    assignment_str += " " + str(-var)
                    counting_vars_iteration_value[var] = 0

        assignments.add(assignment_str)
        # check if assignment is consistent
        sat, model = solver.solve(assumptions)
        outcome = int(sat)
        for var in counting_vars_iteration_value.keys():
            if counting_vars_iteration_value[var] != outcome:
                loss_vector[var] += 1
        if sat:
            positiveSamples += 1
        assumptions = [abs(v) for v in assumptions]
        for var_assignment in assumptions: 
            counting_vars_pos[var_assignment] = loss_vector[var_assignment]

    assignments = set()
    for T in range(min(2**len(counting_vars.keys()), numSamples)):
        # generate random assignment to the counting variables
        assumptions = []
        counting_vars_iteration_value = dict()
        assignment_str = ""
        while assignment_str == "" or assignment_str in assignments:
            assignment_str = ""
            for var in counting_vars.keys():
                if randbool() > 0.5:
                    assumptions.append(var)
                    assignment_str += " " + str(var)
                    counting_vars_iteration_value[var] = 1
                else:
                    assumptions.append(-var)
                    assignment_str += " " + str(-var)
                    counting_vars_iteration_value[var] = 0

        assignments.add(assignment_str)
        # check if assignment is consistent
        sat, model = solver.solve(assumptions)
        outcome = int(sat)
        for var in counting_vars_iteration_value.keys():
            if counting_vars_iteration_value[var] != outcome:
                loss_vector_neg[var] += 1
        if sat:
            positiveSamples += 1
        assumptions = [abs(v) for v in assumptions]
        for var_assignment in assumptions: 
            counting_vars_neg[var_assignment] = loss_vector_neg[var_assignment]
    for key in counting_vars.keys():
        counting_vars[key] = min(counting_vars_pos[key], counting_vars_neg[key])
    return positiveSamples

def countSampleWithMonteCarlo(numMCSamples, counting_vars, clauses):
    solver = solverForSample(clauses)

    # if formula is UNSAT, don't bother sampling
    sat, model = solver.solve()
    if not sat:
        return (0, 0, True)

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

    sampleMant = float(positiveSamples) / numMCSamples
    sampleExp = len(counting_vars.keys())
    while sampleMant > 0 and sampleMant < 1:
        sampleMant *= 2
        sampleExp -= 1
    return (sampleMant, sampleExp, False)

#############################
##### PARTITIONER ###########
#############################

num_clauses_initial = 0
output = ""
counting_vars = dict()
clauses = []
allOne = 0
def get_top_vars(k, numSamples, filename):
    global num_clauses_initial
    #finds top k partitioning variables of formula after c random samples drawn from the counting variables
    var_counts = np.zeros(k)
    global counting_vars
    #get the number of variables and create the appropriate array
    global clauses
    #get the number of positive samples
    global allOne
    counter = 0
    with open(filename, 'r') as f:
        for f_line in f:
            line = f_line.split(' ')
            if "c ind" in f_line:
                ind_vars = line[2:-1]
                counter += 1
                for i in range(len(ind_vars)):
                    counting_vars[int(ind_vars[i])] = 0
            elif line[0] == 'p':
                num_vars_total = int(line[2])
                var_counts = np.zeros(num_vars_total + 1)
                #if no ind vars are specified
            elif line[0] == 'c' and counter != 0:
                continue
            else:
                clauses.append([int(i) for i in line[:-1]])
                counter += 1
    if len(counting_vars.keys()) == 0:
        for i in range(1, len(var_counts)):
            counting_vars[i] = 0
    counter = sample_solutions(numSamples, counting_vars, clauses)
    allOne = (counter == numSamples)
    if counter == 0:
        for i in counting_vars.keys():
            var_counts[i] = 1
    else: 
        for i in counting_vars.keys():
            var_counts[i] = counting_vars[i]
    var_counts = np.argsort(-var_counts)
    var_counts = [v for v in var_counts if v in counting_vars.keys()]
    # print(var_counts)
    return var_counts

def partition_formula(var_counts, filename): 
    n = len(var_counts)
    for index in range(2**n):
        #get binary string corresponding to index
        write_partition(var_counts, filename, index)

def write_partition(var_counts, filename, index, bin_string = None):
    #var counts: an array with index i representing the ith variable to partition on.
    n = len(var_counts)
    b = bin(index)[2:]
    l = len(b)
    b = str(0) * (n - l) + b
    if bin_string is not None:
        b = bin_string
    ##construct constraint
    assignment = ""
    for i in range(len(b)):
        if b[i] == '1':
            assignment += str(var_counts[i]) + ' 0\n'
        else:
            assignment += '-' + str(var_counts[i]) + ' 0\n'
    #add constraint to original file
    with open(filename, 'r') as file:
        data = file.readlines()
    num_data = []
    for i in range(len(data)):
        if "p cnf" in data[i]:
            num_data = data[i].split(' ')
            num_data[-1] = str(int(num_data[-1]) + n) 
            constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
            data[i] = constraints_and_clauses
            break
    ###write modified info back to the file
    name = filename.split('.cnf')[0] + '-window-' + str(index) + '.cnf'
    with open(name, 'w') as f:
        f.writelines(data)
        f.write(assignment)
    f.close()

#################################
##### END PARTITIONER ###########
#################################
if __name__ == "__main__":
    output = str(sys.argv[1])
    try:
        k = int(sys.argv[2])
    except:
        k = 4
    # with open(output + ".cnf", 'r') as f:
    #     data = f.readlines()
    #     with open(output + "copy.cnf", 'w') as filecopy:
    #         filecopy.writelines(data)
    partition_formula(get_top_vars(k, 50000, output), output)

