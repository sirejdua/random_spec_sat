import sys
#try opening up the given file, exit if not possible
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

