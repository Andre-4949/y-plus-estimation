# y+ wall distance estimation tool (like CFD Online)
import math

def _cf_schlichting(Re: float) -> float:
	if Re <= 0:
		raise ValueError("Re must be positive")
	if Re >= 1e9:
		raise ValueError("Re out of range for Schlichting correlation (Re < 1e9)")
	return (2 * math.log10(Re) - 0.65) ** -2.3

def _cf_laminar(Re: float) -> float:
	# Flat plate laminar local skin friction coefficient
	# Cf = 1.328 / sqrt(Re_x)
	if Re <= 0:
		raise ValueError("Re must be positive")
	return 1.328 / math.sqrt(Re)

def estimate_wall_distance(
	u_inf: float,
	rho: float,
	mu: float,
	L: float,
	y_plus: float,
	regime: str = "auto", # 'laminar', 'turbulent', or 'auto'
	transition_Re: float = 5.0e5 # Threshold from Cengel and Cimbala
):
	"""Estimate wall distance for desired y+.

	Parameters
	----------
	u_inf : Freestream velocity [m/s]
	rho : Density [kg/m^3]
	mu : Dynamic viscosity [kg/(m·s)]
	L : Distance from leading edge (local x) [m]
	y_plus : Target y+
	regime : 'laminar', 'turbulent', or 'auto'. In 'auto' choose laminar if Re < transition_Re.
	transition_Re : Threshold Reynolds number for transition decision in 'auto'.
	"""
	Re = rho * u_inf * L / mu
	if regime not in ("laminar", "turbulent", "auto"):
		raise ValueError("regime must be 'laminar', 'turbulent', or 'auto'")

	if regime == "auto":
		active_regime = "laminar" if Re < transition_Re else "turbulent"
	else:
		active_regime = regime

	if active_regime == "laminar":
		Cf = _cf_laminar(Re)
	else:
		Cf = _cf_schlichting(Re)

	tau_w = Cf * 0.5 * rho * u_inf ** 2
	u_tau = math.sqrt(tau_w / rho)
	y = y_plus * mu / (rho * u_tau)
	return {
		'Re': Re,
		'Cf': Cf,
		'tau_w': tau_w,
		'u_tau': u_tau,
		'y': y,
		'regime': active_regime
	}

def calculate_boundary_layer_height(length, Re) -> float:
	if Re <= 0:
		raise ValueError("Reynolds number must be positive")
	if Re < 5e5:
		# Laminar flow
		# Cengel and Cimbala, Fluid Mechanics
		return 4.91 * length / math.sqrt(Re)
	else:
		# Turbulent flow (seventh power law)
		# Cengel and Cimbala, Fluid Mechanics
		return 0.16 * length / Re ** (1/7)
	# else:
		# Turbulent flow ("Obtained from one-seventh-power law combined with empirical data for turbulent flow through smooth pipes" - Cengel and Cimbala)
		# Return roughly the same values yet not exaclty the same as above
		# Commented out 
		# return 0.38 * length / Re ** 0.2


def calculate_prism_layer_cells(total_thickness: float, first_cell_height: float, growth_rate: float) -> int:
	"""Calculate number of prism layer cells needed to reach total thickness.

	Parameters
	----------
	total_thickness : Total thickness of prism layer [m]
	first_cell_height : Height of first prism layer cell [m]
	growth_rate : Growth rate (e.g. 1.2 for 20% growth per layer)

	Returns
	-------
	n : Number of prism layer cells (rounded up)
	"""
	if total_thickness <= 0 or first_cell_height <= 0 or growth_rate <= 1:
		raise ValueError("Invalid input values for prism layer calculation")
	# Geometric series formula rearranged for n
	n = math.ceil(math.log((total_thickness * (growth_rate - 1)) / first_cell_height + 1) / math.log(growth_rate))
	return n

def calculate_all_parameters(length, free_stream_velocity, density, dynamic_viscosity, y_plus_target, growth_rate):

	res = estimate_wall_distance(
		u_inf=free_stream_velocity,
		rho=density,
		mu=dynamic_viscosity,
		L=length,
		y_plus=y_plus_target,
		regime="auto")
	Re = res['Re']
	first_cell_height = res['y']

	total_thickness = calculate_boundary_layer_height(length, Re)

	total_height = calculate_prism_layer_cells(total_thickness, first_cell_height, growth_rate)
	return {
		'wall_distance': first_cell_height,
		'total_boundary_layer_thickness': total_thickness,
		'number_of_prism_layers': total_height,
		'estimation_details': res
	}

def gather_inputs():
	length = float(input("Enter length from leading edge (m): "))
	free_stream_velocity = float(input("Enter free stream velocity (m/s): "))
	
	density = input("Enter fluid density (kg/m^3) [Default: 1.2041]: ")
	if density.strip() == "":
		density = 1.2041  # kg/m^3 for air at 20°C
	else:
		density = float(density)

	dynamic_viscosity = input("Enter dynamic viscosity (kg/(m·s)) [Default: 1.825e-5]: ")
	if dynamic_viscosity.strip() == "":
		dynamic_viscosity = 1.825e-5  # kg/(m·s) for air at 20°C
	else:
		dynamic_viscosity = float(dynamic_viscosity)
	y_plus_target = float(input("Enter target y+: "))
	growth_rate = float(input("Enter growth rate (>1): "))
	return length, free_stream_velocity, density, dynamic_viscosity, y_plus_target, growth_rate

if __name__ == "__main__":
	length, free_stream_velocity, density, dynamic_viscosity, y_plus_target, growth_rate = gather_inputs()
	results = calculate_all_parameters(
		length,
		free_stream_velocity,
		density,
		dynamic_viscosity,
		y_plus_target,
		growth_rate
	)
	print()
	print("Estimated Wall Distance (y+): {:.6f} m".format(results['wall_distance']))
	print("Total Boundary Layer Thickness: {:.6f} m".format(results['total_boundary_layer_thickness']))
	print("Number of Prism Layer Cells: {}".format(results['number_of_prism_layers']))
	print("In Star-CCM+, set the total thickness to {} meters, the number of layers to {}, and the growth rate to {}.".format(
		results['total_boundary_layer_thickness'],
		results['number_of_prism_layers'],
		growth_rate
	))
	# print("\nEstimation Details:")
	# for key, value in results['estimation_details'].items():
	# 	print("  {}: {}".format(key, value))