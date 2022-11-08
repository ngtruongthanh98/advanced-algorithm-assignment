# !python3 main.py < input.txt > output.txt
# MIP (Mixed Integer Programming) problem
from ortools.linear_solver import pywraplp
from vessel import Vessel

import sys

tmp = sys.stdin.readline().rstrip('\n').split(' ')
S = float(tmp[0]) #Berth lenght
T = float(tmp[1]) #Total time
tmp = sys.stdin.readline().rstrip('\n')
K = int(tmp) #Number of breaks points
b = [0] * K

for i in range(K):
	tmp = sys.stdin.readline().rstrip('\n')
	b[i] = float(tmp)

b.sort()

tmp = sys.stdin.readline().rstrip('\n')
N = int(tmp) #Number of vessels
vessels = []
w = [0] * N
a = [0] * N
s = [0] * N
p = [0] * N
idx = [0] * N # unuse for calculate

for i in range(N):
	tmp = sys.stdin.readline().rstrip('\n').split(' ')
	idx[i] = int(tmp[0])
	s[i] = float(tmp[1])
	a[i] = float(tmp[2])
	p[i] = float(tmp[3])
	if len(tmp) == 5:
		w[i] = int(tmp[4])
	else:
		w[i] = 1
	
	vessels.append(Vessel(idx[i], s[i], a[i], p[i], w[i]))



print("Berth length: ", S)
print("Total time: ", T)
print("Number of breaks: ", K)
for i in range(K):
	print("Break ", i, ": ", b[i])
print("Number of vessels: ", N)
for i in range(N):
	print(vessels[i])

# validate input:
# Berth breaks sorted ascending and >= 0 and <= S
# Vessel index is unique
# S,T,K,N >=0

# Create the mip solver with the SCIP backend.
# solver = pywraplp.Solver.CreateSolver('SCIP')
# CBC_MIXED_INTEGER_PROGRAMMING or CBC (free)
# SCIP_MIXED_INTEGER_PROGRAMMING or SCIP(free) (****)

# GLPK_MIXED_INTEGER_PROGRAMMING or GLPK or GLPK_MIP (license)
# GUROBI_MIXED_INTEGER_PROGRAMMING or GUROBI or GUROBI_MIP (license)
# CPLEX_MIXED_INTEGER_PROGRAMMING or CPLEX or CPLEX_MIP (license)
# XPRESS_MIXED_INTEGER_PROGRAMMING or XPRESS or XPRESS_MIP (license)

# Support for {} not linked in, or the license was not found.
solver = pywraplp.Solver.CreateSolver('SCIP')
# solver = pywraplp.Solver('Maximize army power', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
if not solver:
	exit (1)

infinity = solver.infinity()
u = [None]*N
v = [None]*N
c = [None]*N
sigma = [[None]*N]*N #1: i left j (i != j)
delta = [[None]*N]*N #1: i below j (i != j)
gamma = [[None]*K]*N #1: v_i >= b_k

num_vars = 3*N + 2*N**2 + N*K

# Declare variables: 3*N + 2*N^2 + N*K
for i in range(N):
	u[i] = solver.NumVar(0, infinity, 'u[%i]' % i)
	v[i] = solver.NumVar(0, infinity, 'v[%i]' % i)
	c[i] = solver.NumVar(0, infinity, 'c[%i]' % i)
	for j in range(N):
		if i != j:
			sigma[i][j] = solver.IntVar(0, 1, f'sigma[{i},{j}]')
			delta[i][j] = solver.IntVar(0, 1, f'delta[{i},{j}]')
	for k in range(K):
		gamma[i][k] = solver.IntVar(0, 1, f'gamma[{i},{k}]')


# Objective function: The result need to subtract w_i*a_i (constant)
objective = solver.Objective()
for i in range(N):
	objective.SetCoefficient(c[i], w[i])
# objective.SetMaximization()
objective.SetMinimization()


# Constraints
for i in range(N):
	for j in range(N):
		if i != j:
			constraint = solver.RowConstraint(-p[i], T-p[i], f'Sigma of {i} and {j}')
			constraint.SetCoefficient(u[i], 1)
			constraint.SetCoefficient(u[j], -1)
			# constraint.SetCoefficient(p[i], 1)
			constraint.SetCoefficient(sigma[i][j], T)


			constraint = solver.RowConstraint(-s[i], S-s[i], f'Delta of {i} and {j}')
			constraint.SetCoefficient(v[i], 1)
			constraint.SetCoefficient(v[j], -1)
			# constraint.SetCoefficient(s[i], 1)
			constraint.SetCoefficient(delta[i][j], S)
		
			# constraint = solver.RowConstraint(0, 1, f'Sigma overlap of {i} and {j}')
			# constraint.SetCoefficient(sigma[i][j], 1)
			# constraint.SetCoefficient(sigma[j][i], 1)

			# constraint = solver.RowConstraint(0, 1, f'Delta overlap of {i} and {j}')
			# constraint.SetCoefficient(delta[i][j], 1)
			# constraint.SetCoefficient(delta[j][i], 1)

			constraint = solver.RowConstraint(1, 2, f'Sigma and Delta overlap of {i} and {j}')
			constraint.SetCoefficient(sigma[i][j], 1)
			constraint.SetCoefficient(sigma[j][i], 1)
			constraint.SetCoefficient(delta[i][j], 1)
			constraint.SetCoefficient(delta[j][i], 1)
		
	constraint = solver.RowConstraint(p[i], p[i], f'Start, Process and End of {i}')
	constraint.SetCoefficient(c[i], 1)
	constraint.SetCoefficient(u[i], -1)
	# constraint.Add(c[i] + u[i] == p[i])

	constraint = solver.RowConstraint(a[i], T-p[i], f'Start time of vessel {i}')
	constraint.SetCoefficient(u[i], 1)

	constraint = solver.RowConstraint(0, S-s[i], f'Location of vessel {i}')
	constraint.SetCoefficient(v[i], 1)

	
	
	# # if x in range b[k] and b[k+1] (x have v[i] and v[i] + s[i] in same range)
	# # -S+b[k] <= x - S*gamma[i][k] <= b[k]
	# # -S+b[k] <= v[i] - S*gamma[i][k] <= b[k]
	# # -S+b[k] <= v[i] + s[i] - S*gamma[i][k] <= b[k]
	# # =>  -S+b[k] <= v[i] - S*gamma[i][k] <= b[k] - s[i]
	# for k in range(K):
	# 	constraint = solver.RowConstraint(-S+b[k], b[k]-s[i], f'Gamma the range of start vessel {i} compare to break {k}')
	# 	constraint.SetCoefficient(v[i], 1)
	# 	constraint.SetCoefficient(gamma[i][k], -S)

	# 	# gamma[i] = 1 if v_i >= b_k
	# 	# Sort array: b[i] >= b[i+1] (i = 0,1,...,K-2) 1->0
	# 	# Gamma
	# 	if k > 0:
	# 		constraint = solver.RowConstraint(0, 1, f'Gamma relation of {k-1} and {k} in vessel {i}')
	# 		constraint.SetCoefficient(gamma[i][k-1], 1)
	# 		constraint.SetCoefficient(gamma[i][k], -1)

status = solver.Solve()


if status == pywraplp.Solver.OPTIMAL:
	# obj_value = solver.Objective().Value()
	print("************************************")
	print("**** Result of optimal solution ****")
	print("************************************")
	

	result = solver.Objective().Value()
	for i in range(N):
		result -= w[i]*a[i]

	print('Objective value =', solver.Objective().Value())
	print('Final result value =', result)
	for i in range(N):
		vessels[i].set_solution(
			start_time = u[i].solution_value(),
			end_time = u[i].solution_value() + p[i],
			start_berth = v[i].solution_value(),
			end_berth = v[i].solution_value() + s[i]
		)
		print(vessels[i])
	
	print("\n**** Sigma[i][j]: 1-Left ****")
	for i in range(N):
		for j in range(N):
			if i != j:
				print(int(sigma[i][j].solution_value()), end=' ')
			else:
				print('_', end=' ')
		print()


	print("\n**** Delta[i][j]: 1-Below ****")
	for i in range(N):
		for j in range(N):
			if i != j:
				print(int(delta[i][j].solution_value()), end=' ')
			else:
				print('_', end=' ')
		print()


	print("\n**** Gamma[i][k]: v[i]>=b[k] ****")
	for i in range(N):
		for k in range(K):
			print(int(gamma[i][k].solution_value()), end=' ')
		print()
	
	print("\n**** Solver information ****")
	print('Number of variables =', solver.NumVariables())
	print('Number of constraints =', solver.NumConstraints())
	print('Problem solved in %f milliseconds' % solver.wall_time())
	print('Problem solved in %d iterations' % solver.iterations())
	print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
else:
	print('The problem does not have an optimal solution.')
 