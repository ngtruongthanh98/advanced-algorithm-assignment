# 1910663
from docplex.mp.model import Model
from docplex.mp.progress import *
from vessel import Vessel

import sys

orig_stdout = sys.stdout
f = open('output.txt', 'w')
sys.stdout = f

##########################
# Handle input parameters
##########################

tmp = sys.stdin.readline().rstrip('\n').split(' ')
S = int(tmp[0]) #Berth length
T = float(tmp[1]) #Total time
tmp = sys.stdin.readline().rstrip('\n')
K = int(tmp) #Number of breaks points
b = [0] * K #Break point

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
idx = [0] * N 

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


### Validate input
if not (S >= 0 and T >= 0 and K >= 0 and N >= 0):
	print("Invalid input negative value")
	exit(1)

for i in range(K+2):
	if not (b[i] >= 0 and b[i] <= S):
		print("Invalid input breaks")
		exit(1)

if len(idx) != len(set(idx)):
	print("Invalid vessel input duplicate")
	exit(1)

# Print input
print("************************************")
print("********** Input parameters ********")
print("************************************")
print("Berth length: ", S)
print("Total time: ", T)
print("Number of breaks: ", K)
for i in range(K+2):
	print("Break ", i, ": ", b[i])
print("Number of vessels: ", N)
for i in range(N):
	print(vessels[i])
print()



# Set up Solver
solver = Model(name='Min loss')
if not solver:
	exit (1)

# Declare variables
infinity = solver.infinity
u = [None]*N
v = [None]*N

for i in range(N):
	u[i] = solver.integer_var(name='u[%i]' % i)
	v[i] = solver.integer_var(name='v[%i]' % i)

# Objective function: We don't need c[i]
solver.set_objective("min", solver.sum(w[i]*(u[i]-a[i]) for i in range(N)))


# Constraints
for i in range(N):
	for j in range(N):
		if i > j:
			# 2 rectangle overlap
			solver.add_constraint(solver.logical_or(
				u[i] >= u[j] + p[j], 
				u[j] >= u[i] + p[i],
				v[j] >= v[i] + s[i],
				v[i] >= v[j] + s[j]
			) == 1)
	
	solver.add_constraint(u[i] >= a[i], ctname=f'Start, Process and End of Vessel {i} lower bound')
	solver.add_constraint(u[i] <= T-p[i], ctname=f'Start, Process and End of Vessel {i} upper bound')

	solver.add_constraint(v[i] <= S-s[i], ctname=f'Location of vessel {i}')

	for k in range(1,K+2):
		solver.add_if_then(solver.logical_and(v[i]>=b[k-1], v[i]<=b[k]-1) == 1, solver.logical_and(v[i]+s[i]>=b[k-1]+1, v[i]+s[i]<=b[k]) == 1)



print("************************************")
print("******** Solver information ********")
print("************************************")
solver.print_information()


# Print solution
print("\n\n\n")
print("************************************")
print("**** Result of optimal solution ****")
print("************************************")
try:
	sol = solver.solve(log_output=False)
	# solver.print_solution()
	print("Objective value =",sol.get_objective_value())
	print("**** Time ****")
	for i in range(N):
		print(u[i].solution_value, end=' ')

	print("\n**** Berth ****")
	for i in range(N):
		print(v[i].solution_value, end=' ')

	print("\n**** Process ****")
	for i in range(N):
		print(p[i], end=' ')

	print("\n**** Vessel infomation ****")
	for i in range(N):
		vessels[i].set_solution(
			start_time = u[i].solution_value,
			end_time = u[i].solution_value + p[i],
			start_berth = v[i].solution_value,
			end_berth = v[i].solution_value + s[i]
		)
		print(vessels[i])
except:
	print('\nThe problem does not have an optimal solution.')




# Pipe redirect to output.txt
sys.stdout = orig_stdout
f.close()


# Draw plot
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111)

# Draw breaks
for i in range(1,K+2):
	plot( [0,T] ,[b[i],b[i]], '-', linewidth = 2)

# Grid
grid(color='b', linestyle='-', linewidth=0.7, alpha=0.4)

# Bright color
low = 0.6
high = 0.95
for i in range(N):
	rgb = (np.random.uniform(low=low, high=high),
                    np.random.uniform(low=low, high=high),
                    np.random.uniform(low=low, high=high))
	rect=mpatches.Rectangle((u[i].solution_value,v[i].solution_value),
							p[i],s[i], 
							fill = True,
							facecolor=rgb,
							edgecolor='black',
							linewidth = 1,
							zorder=4)
	plt.gca().add_patch(rect)
	plot( [a[i],a[i]] ,[0,S], linestyle='dashed',c=rgb, linewidth = 1.5)

	rx, ry = rect.get_xy()
	cx = rx + rect.get_width()/2.0
	cy = ry + rect.get_height()/2.0
	ax.annotate(str(vessels[i].idx), (cx, cy), color='black', weight='bold', fontsize=10, ha='center', va='center', zorder=5)


# Draw Ox, Oy axis
left,right = ax.get_xlim() 
low,high = ax.get_ylim() 
arrow( left, 0, right -left, 0, length_includes_head = True, head_width = 0.55 )
arrow( 0, low, 0, high-low, length_includes_head = True, head_width = 0.55 ) 

# Show grid
show()