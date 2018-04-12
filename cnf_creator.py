import sys, os, subprocess
from shutil import copyfile
#try opening up the given file, exit if not possible
count = False
try:
    f = open(str(sys.argv[1]), 'r')
except:
    print("No file named " + str(sys.argv[1]))
    sys.exit()

#assemble the variable and clauses list
clauses = []
variables = dict()
counter = 1
for line in f:
    line = line.strip(' ,')
    #add clauses to list
    line = line.strip("Or").strip("()\n")
    clauses += [line]
    #add variables to set
    line_vars = line.split(', ')
    for var in line_vars:
        var = var.strip("Not()\n,")
        if var not in variables:
            variables[var] = counter
            counter += 1
f.close()
print(len(clauses))
#after obtaining the variable and clause sets...construct the file
if len(sys.argv) >= 3:
    output = str(sys.argv[2])
else:
    output = str(sys.argv[1]).split('.')[0] 
with open(output + ".cnf", 'w') as f:
    f.write('c ' + str(sys.argv[1]) + "\n")
    f.write('c\n')
    f.write('p cnf ' + str(len(variables.keys())) + ' ' + str(len(clauses)) + "\n")
    for clause in clauses:
        clause_vars = clause.split(', ')
        line = ""
        for var in clause_vars:
            if var[0] == "N":
                line += "-"
            var = var.strip("Not()\n,")
            #get the number corresponding to the actual variable
            var = variables[var]
            line = line + str(var) + ' '
        line += "0"
        f.write(line + "\n")
    f.close()

################## 
# MODEL COUNTING #
##################
def count_model():
    counter = 0
    all_found = False
    while not all_found:
        #kind of hackish but meh
        os.system('minisat modelcpy.cnf model-sol.cnf')
        with open('model-sol.cnf', 'r') as sol_file:
            status = sol_file.readline()
            if 'UNSAT' not in status:
                #if there exists a solution....
                assignments = sol_file.readline().split(' ')[:-1]
                new_assignments = []
                ##construct constraint
                for i in range(len(assignments)):
                    if assignments[i][0] == '-':
                        new_assignments += [assignments[i][1:]]
                    else:
                        new_assignments += ['-' + assignments[i]]
                assignment = ""
                for k in new_assignments:
                    assignment = assignment + k + ' '
                assignment += '0\n'
                #add constraint to original file
                with open('modelcpy.cnf', 'r') as file:
                    data = file.readlines()
                num_data = data[2].split(' ')
                num_data[-1] = str(int(num_data[-1]) + 1) 
                constraints_and_clauses = num_data[0] + ' ' + num_data[1] + ' ' + num_data[2] + ' ' + num_data[3] + '\n'
                data[2] = constraints_and_clauses
                ###write modified info back to the file banning this last solution and adjusting the number of clauses
                with open('modelcpy.cnf', 'w') as file:
                    file.writelines(data)
                    file.write(assignment)
                counter += 1
            else:
                all_found = True
    return counter

##################################
if count == True:
    count_model
    print(counter)