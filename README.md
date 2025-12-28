# y+ Wall Distance Calculator

A Python tool for calculating wall distance and prism layer parameters for CFD mesh generation. This helps you figure out the first cell height and number of prism layers needed to capture the boundary layer properly.

## What it does

The script calculates:

- First cell height for a target y+ value
- Boundary layer thickness (using correlations from Cengel and Cimbala)
- Number of prism layers needed to cover the boundary layer

It automatically determines whether the flow is laminar or turbulent based on Reynolds number (transition at Re = 5×10^5). For turbulent flow, it uses the Schlichting skin friction correlation.

## Usage

Run the script and provide:

- Length from leading edge (m)
- Free stream velocity (m/s)
- Fluid density (kg/m³) - defaults to air at 20°C
- Dynamic viscosity (kg/(m·s)) - defaults to air at 20°C
- Target y+
- Growth rate for prism layers (e.g., 1.2 for 20% growth)

The output includes parameters ready to use in Star-CCM+ or similar CFD software.

## Example

The typical side wing of a formula student race car is around 1 to 1.2 meters in legnth (I will assume 1 meter). Assuming a free stream velocity of 15 m/s on the straight, we can calculate the wall distance and prism layers as follows:

```plaintext
Enter length from leading edge (m): 1
Enter free stream velocity (m/s): 15
Enter fluid density (kg/m^3) [Default: 1.2041]:
Enter dynamic viscosity (kg/(m·s)) [Default: 1.825e-5]:
Enter target y+: 1
Enter growth rate (>1): 1.2

Estimated Wall Distance (y+): 0.000023 m
Total Boundary Layer Thickness: 0.022265 m
Number of Prism Layer Cells: 29
In Star-CCM+, set the total thickness to 0.022264927022660624 meters, the number of layers to 29, and the growth rate to 1.2.
```

You may just press enter to use the default values for density and viscosity. Adjust these to the conditions of your specific case if you are planning on determining the deviation.

## Notes

- Valid for Reynolds numbers below 1×10⁹
- Uses flat plate boundary layer assumptions 
- Turbulent correlation from Schlichting (1979)
- Laminar skin friction: Cf = 1.328 / √Re
