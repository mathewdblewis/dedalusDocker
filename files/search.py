import numpy as np; import os
import json
from makeSolver import makeSolver
import matplotlib.pyplot as plt
import h5py
from numpy import array as ar
from os import system
from dedalus.extras import flow_tools
from multiprocessing import Pool

minRa = 720


def breakCond(file):
	timePeriodAvg,ratio,cutTime = 10,.5,50
	k = timePeriodAvg
	Q = [np.array([sum(a) for a in [[float(y) for y in x] for x in l]]) for l in file['tasks']['yvel']]
	SQ = [sum(Q[t:t+k])/k for t in range(len(Q)-k)]
	jets = [[1 if t>max(s)*ratio else 0 for t in s] for s in SQ]
	numJets = [sum([abs(j[i]-j[i+1])/2 for i in range(len(j)-1)]) for j in jets]
	return not (True in [n==1 for n in numJets[-cutTime:]])


def run(x,d,stepsPerOrder,origin,num_time_steps):

	# x = (Ra_exp,Pr_exp)
	y = x+d
	
	name_x = "run_%s,%s" % (str(x[0]).zfill(5),str(x[1]).zfill(5))
	name_y = "run_%s,%s" % (str(y[0]).zfill(5),str(y[1]).zfill(5))

	
	probParams = {"Ra":100000,"Pr":1,"res":20,"total_run_time":100,"dt":.02,"Lx":20,"Lz":1,"flow_bc":"no-slip","temp_bc":"fixed-flux"}
	probParams['Ra'], probParams['Pr'] = 10**(y[0]/stepsPerOrder[0])*origin[0], 10**(y[1]/stepsPerOrder[1])*origin[1]
	if probParams['Ra']<minRa: return True
	
	print("\n\n **********\n Starting simulation for (%d,%d) from (%d,%d)" % (y[0],y[1],x[0],x[1]))
	print(" For this simulation we have:  Ra,Pr = %f,%f\n **********" % (probParams['Ra'],probParams['Pr']))

	if os.path.exists('output/%s_snap' % name_y):
		print('****** already exists! ******\n\n')
	else:
		print('\n\n')
		solver = makeSolver(probParams)
		snapshots = solver.evaluator.add_file_handler('output/%s_snap'  % name_y, iter=100,  max_writes=1000, mode='append')
		state	 = solver.evaluator.add_file_handler('output/%s_state' % name_y, iter=num_time_steps, max_writes=1000, mode='append')
		snapshots.add_task("T-(z-1/2)", name = 'temp')
		snapshots.add_task("w", name = 'yvel')
		state.add_system(solver.state)

		restart_path = 'output/%s_state/%s_state_s1/%s_state_s1_p0.h5' % ((name_x,)*3)
		solver.load_state(restart_path, -1)
		
		solver.stop_sim_time = solver.sim_time+probParams['total_run_time']


		dt = probParams['dt']
		CFL = flow_tools.CFL(solver, initial_dt=dt, cadence=10, safety=0.5,max_change=1.5, min_change=0.5, max_dt=0.125, threshold=0.05)
		CFL.add_velocities(('u', 'w'))

		for _ in range(num_time_steps+1):
			dt = CFL.compute_dt()
			dt = solver.step(dt)
			if (solver.iteration-1) % 50 == 0:
				open('progress.txt','w').write('%d/%d\n' % (solver.sim_time , solver.stop_sim_time))

	# return True if the break condition has been met, regardless if you just ran the simulation or not
	file = h5py.File('output/%s_snap/%s_snap_s1/%s_snap_s1_p0.h5' % ((name_y,)*3), mode='r')
	B = breakCond(file)
	print('break condition: ', B)
	return B



stepsPerOrder = ar((16,16))		# steps per order of magnitude in the Ra and Pr parameters
origin = ar((10**5,1))			# the value of (Ra,Pr) that the simulation starts at
num_time_steps = 2000			# the number of steps to take in time, step size determined by the CFL condition




# create the directories for the initial state
# then copy in the restart file
name = "run_00000,00000"
system("mkdir output/")
system('mkdir output/%s_state' % name)
system('mkdir output/%s_state/%s_state_s1' % ((name,)*2))
system("cp restart.h5 output/%s_state/%s_state_s1/%s_state_s1_p0.h5" % ((name,)*3))
# create the json file of explored nodes
open('output/region.json','w').write('[[0,0]]')

run(ar((0,0)),ar((0,1)),stepsPerOrder,origin,num_time_steps)



