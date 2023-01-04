from dedalus import public as de
import numpy as np

def makeSolver(p):
	Lx,Lz,flow_bc,temp_bc,Ra,Pr,res = p['Lx'],p['Lz'],p['flow_bc'],p['temp_bc'],p['Ra'],p['Pr'],p['res']
	# Create bases and domain
	nx, nz = Lx*res, Lz*res
	x_basis = de.Fourier('x', nx, interval=(0, Lx), dealias=3/2)
	z_basis = de.Chebyshev('z', nz, interval=(-Lz/2, Lz/2), dealias=3/2)
	domain = de.Domain([x_basis, z_basis], grid_dtype=np.float64)

	# Problem setup: 2D Boussinesq equations; non-dimensionalized by the buoyancy time
	# and written in terms of the vorticity
	problem = de.IVP(domain, variables=['p','T','u','w','Tz','oy','avg_wT','avg_K','avg_T','avg_T_sq','avg_u_sq','avg_w_sq'])
	problem.meta['p','T','u','w']['z']['dirichlet'] = True
	problem.meta['avg_T','avg_u_sq','avg_w_sq','avg_T_sq','avg_wT','avg_K']['x']['constant'] = True

	problem.parameters['P'] = (Ra * Pr)**(-1/2)
	problem.parameters['R'] = (Ra / Pr)**(-1/2)
	problem.parameters['F'] = F = 1
	problem.parameters['kappa_xz'] = 1/(Lx*Lz)
	problem.parameters['kappa_x'] = 1/Lx

	# zero divergence
	problem.add_equation("dx(u) + dz(w) = 0")
	# T' = ...
	problem.add_equation("dt(T) - P*(d(T,x=2) + dz(Tz)) - F*w  = -(u*dx(T) + w*Tz)")
	# u' = ...
	problem.add_equation("dt(u) - R*dz(oy)    + dx(p)          = -oy*w")
	problem.add_equation("dt(w) + R*dx(oy)    + dz(p)   - T    =  oy*u")
	# defining Tz
	problem.add_equation("Tz - dz(T) = 0")
	# defining oy
	problem.add_equation("oy + dx(w) - dz(u) = 0")

	# time integrals of various quantities for calculating Nu and Re
	problem.add_equation("dt(avg_wT)   = kappa_xz*integ_z(integ_x(w*(T+1/2-z)))")
	problem.add_equation("dt(avg_K)    = kappa_xz*integ_z(integ_x(u**2+w**2))")
	problem.add_equation("dt(avg_T)    = kappa_x*integ_x(T)")
	problem.add_equation("dt(avg_u_sq) = kappa_x*integ_x(u**2)")
	problem.add_equation("dt(avg_w_sq) = kappa_x*integ_x(w**2)")
	problem.add_equation("dt(avg_T_sq) = kappa_x*integ_x(T**2)")


	if temp_bc == 'fixed-flux':
	    problem.add_bc("left(Tz) = 0")
	    problem.add_bc("right(Tz) = 0")
	elif temp_bc == 'fixed-temp':
	    problem.add_bc("left(T) = 0")
	    problem.add_bc("right(T) = 0")
	else:
	    print('invalid temp_bc')
	    exit(1)
	if flow_bc == "no-slip":
	    problem.add_bc("left(u) = 0")
	    problem.add_bc("right(u) = 0")
	elif flow_bc == "stress-free":
	    problem.add_bc("left(oy) = 0")
	    problem.add_bc("right(oy) = 0")
	else:
	    print('invalid flow_bc')
	    exit(1)

	problem.add_bc("left(w) = 0")
	problem.add_bc("right(w) = 0", condition="(nx != 0)")
	problem.add_bc("right(p) = 0", condition="(nx == 0)")

	return problem.build_solver(de.timesteppers.RK222)
