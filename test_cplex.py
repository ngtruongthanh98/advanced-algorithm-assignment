from docplex.mp.model import Model
from docplex.mp.progress import *
from vessel import Vessel

import sys



tmp = sys.stdin.readline().rstrip('\n').split(' ')
S = int(tmp[0]) #Berth lenght
T = float(tmp[1]) #Total time
tmp = sys.stdin.readline().rstrip('\n')
K = int(tmp) #Number of breaks points
b = [0] * K

for i in range(K):
	tmp = sys.stdin.readline().rstrip('\n')
	b[i] = int(tmp)

b.sort()
b.insert(0,0)
b.append(S)

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
for i in range(K+2):
	print("Break ", i, ": ", b[i])
print("Number of vessels: ", N)
for i in range(N):
	print(vessels[i])


solver = Model(name='Min loss')
if not solver:
	exit (1)

infinity = solver.infinity

u = [None]*N
v = [None]*N
c = [None]*N
sigma = [[None]*N]*N #1: i left j (i != j)
delta = [[None]*N]*N #1: i below j (i != j)
gamma = [[None]*K]*N #1: v_i >= b_k

num_vars = 3*N + 2*N**2 + N*K
tmp = [[[None]*4]*N]*N

# Declare variables: 3*N + 2*N^2 + N*K
for i in range(N):
	u[i] = solver.integer_var(name='u[%i]' % i)
	v[i] = solver.integer_var(name='v[%i]' % i)
	# c[i] = solver.continuous_var(name='c[%i]' % i)
	# for j in range(N):
		# for ll in range(4):
		# 	tmp[i][j][ll] = solver.binary_var(name='tmp[%i][%i][%i]' % (i, j, ll))
		# if i != j:
		# 	sigma[i][j] = solver.binary_var(name=f'sigma[{i},{j}]')
		# 	delta[i][j] = solver.binary_var(name=f'delta[{i},{j}]')
	for k in range(K):
		gamma[i][k] = solver.binary_var(name=f'gamma[{i},{k}]')


# Objective function: The result need to subtract w_i*a_i (constant)
solver.set_objective("min", solver.sum(w[i]*(u[i]-a[i]) for i in range(N)))

# for k in range(1, K+2)

# solver.add_if_then(solver.logical_and(v[1] >= b[0], v[1] <= 12 ) == 1, solver.logical_and(gamma[0][0] == 0, gamma[0][1] == 0) == 1)
# solver.add_if_then(solver.logical_and(v[i]>=b[k-1], v[i]<=b[k]-1) == 1, gamma[i][k] == 1)
# v[1]<=b[2]
# Constraints
for i in range(N):
	for j in range(N):
			# solver.add_if_then(sigma[i][j]==1, u[i]+p[i]<=u[j]-1)
			# solver.add_if_then(sigma[i][j]==0, u[i]+p[i]>=u[j])


			# solver.add_if_then(delta[i][j]==1, v[i]+s[i]<=v[j])
			# solver.add_if_then(delta[i][j]==0, v[i]+s[i]>=v[j])

			# solver.add_constraint(u[j]-u[i]-p[i]-(sigma[i][j]-1)*T >= 0, ctname=f'Sigma of {i} and {j}')

			
			# solver.add_constraint(v[j]-v[i]-s[i]-(delta[i][j]-1)*S >= 0, ctname=f'Delta of {i} and {j}')
	
		
			# solver.add_constraint(sigma[i][j] + sigma[j][i] <= 1, ctname=f'Sigma overlap of {i} and {j}')

			# solver.add_constraint(delta[i][j] + delta[j][i] <= 1, ctname=f'Delta overlap of {i} and {j}')

			
			# solver.add_constraint(sigma[i][j] + sigma[j][i] + delta[i][j] + delta[j][i] >= 1, ctname=f'Sigma and Delta overlap of {i} and {j}')
		if i > j:
			# solver.add_if_then( (u[i] >= (u[j] + p[j])), tmp[i][j][0]==1)
			# solver.add_constraint(tmp[i][j][0]==(u[i] >= (u[j] + p[j])))
			# solver.add_constraint(tmp[i][j][1]==((u[i] + p[i]) <= u[j]))
			# solver.add_constraint(tmp[i][j][2]==((v[i] + s[i]) <= v[j]))
			# solver.add_constraint(tmp[i][j][3]==(v[i] >= (v[j] + s[j])))
			# u[i] >= u[j] + p[j], 
			# u[j] >= u[i] + p[i],
			# v[j] >= v[i] + s[i],
			# v[i] >= v[j] + s[j]
			# 2 rectangle overlap
			solver.add_constraint(solver.logical_or(
				u[i] >= u[j] + p[j], 
				u[j] >= u[i] + p[i],
				v[j] >= v[i] + s[i],
				v[i] >= v[j] + s[j]
			) == 1)
	
	# solver.add_constraint(u[i] + p[i] == c[i], ctname=f'Start, Process and End of Vessel {i}')


	solver.add_constraint(u[i] >= a[i], ctname=f'Start, Process and End of Vessel {i} lower bound')
	solver.add_constraint(u[i] <= T-p[i], ctname=f'Start, Process and End of Vessel {i} upper bound')


	solver.add_constraint(v[i] <= S-s[i], ctname=f'Location of vessel {i}')

	for k in range(1,K+2):
		# solver.add_constraint(solver.logical_or(
		# 	gamma[i][k-1] == 0,
		# 	v[i] >= b[k-1]
		# ) == 1)
# 
		solver.add_if_then(solver.logical_and(v[i]>=b[k-1], v[i]<=b[k]-1) == 1, solver.logical_and(v[i]+s[i]>=b[k-1]+1, v[i]+s[i]<=b[k]) == 1)
	
	# 	solver.add_constraint(v[i] - S*gamma[i][k] >= -S+b[k], ctname=f'Gamma the range of start vessel {i} compare to break {k}')
	# 	solver.add_constraint(v[i] - S*gamma[i][k] <= b[k]-s[i], ctname=f'Gamma the range of start vessel {i} compare to break {k}')

	# 	if k > 0:
	# 		solver.add_constraint(gamma[i][k-1] >= gamma[i][k], ctname=f'Gamma relation of {k-1} and {k} in vessel {i}')



# a.solution_value

# Print solution
solver.print_information()



# print("************************************")
# print("**** Result of optimal solution ****")
# print("************************************")


# solver.parameters.mip.limits.solutions=1

# while True:
sol = solver.solve(log_output=False)
# solver.print_solution()
print("\n\nobjective =",sol.get_objective_value())
print("**** Time ****")
for i in range(N):
	print(u[i].solution_value, end=' ')


print("\n**** Berth ****")
for i in range(N):
	print(v[i].solution_value, end=' ')

print("\n**** Process ****")
for i in range(N):
	print(p[i], end=' ')

print()
for i in range(N):
	vessels[i].set_solution(
		start_time = u[i].solution_value,
		end_time = u[i].solution_value + p[i],
		start_berth = v[i].solution_value,
		end_berth = v[i].solution_value + s[i]
	)
	print(vessels[i])

# print("\n**** Sigma[i][j]: 1-Left ****")
# for i in range(N):
# 	for j in range(N):
# 		if i != j:
# 			print(int(sigma[i][j].solution_value), end=' ')
# 		else:
# 			print('_', end=' ')
# 	print()


# print("\n**** Delta[i][j]: 1-Below ****")
# for i in range(N):
# 	for j in range(N):
# 		if i != j:
# 			print(int(delta[i][j].solution_value), end=' ')
# 		else:
# 			print('_', end=' ')
# 	print()


print("\n**** Gamma[i][k]: v[i]>=b[k] ****")
for i in range(N):
	for k in range(K):
		print(int(gamma[i][k].solution_value), end=' ')
	print()

# 	# break
# # print("\n**** Solver information ****")
# # print('Number of variables =', solver.NumVariables())
# # print('Number of constraints =', solver.NumConstraints())
# # print('Problem solved in %f milliseconds' % solver.wall_time())
# # print('Problem solved in %d iterations' % solver.iterations())
# # print('Problem solved in %d branch-and-bound nodes' % solver.nodes())


