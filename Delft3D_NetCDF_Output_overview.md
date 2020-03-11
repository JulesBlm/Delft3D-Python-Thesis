# Delft3D NetCDF output keywords

## Vector components
| Keywords set | Description | Dimensions U/ $\xi$ | Dimensions V/ $\eta$ |
|--------------|-------------|--------------|-------------|
| U1, V1 | U, V velocity per layer in U, V point   | (time, KMAXOUT_RESTR, MC, N) | (time, KMAXOUT_RESTR, M, NC) |
| SBUU, SBVV | Bed-load transport in u,v-direction (u point) (v point) | (time, LSEDTOT, MC, N) |  (time, LSEDTOT, M, NC) |
| SSUU, SSVV | Suspended-load transport  in u,v-direction (u point) (v point) | (time, LSED, MC, N) | (time, LSED, M, NC) |
| TAUKSI, TAUETA | Bottom stress in U,V - point | (time, MC, N) |  (time, M, NC) |
| SBUUA, SBVVA | Stat stuff: Average bed-load transport  | (avgtime, LSEDTOT, MC, N) | (avgtime, LSEDTOT, M, NC) |
| SSUUA, SSVVA | Stat stuff: Average suspended-load transport | (avgtime, LSEDTOT, MC, N) |(avgtime, LSEDTOT, MC, N)|

# Most important for me
| Keyword | Description |Dimensions|
|-----------|-------------|-------------|
| RHO   | Density per layer in sigma point | (time, KMAXOUT_RESTR, M, N) |
| WPHY  | W-velocity per layer in sigma point | (time, KMAXOUT_RESTR, M, N) |
| W   | W-omega per layer in sigma point ANGLE | (time, KMAXOUT, M, N) |
| R1  | Concentrations per layer in sigma point | (time, LSTSCI, KMAXOUT_RESTR, M, N) |
| WS  | Settling velocity per sigma-layer | (time, LSED, KMAXOUT, M, N) |

## Bottom surface properties
| Keyword | Description | Dimensions|
|-----------|-------------|---------|
| DM        | Arithmetic mean sediment diameter | (time, M, N) |
| DG        | Geometric mean sediment diameter | (time, M, N) |
| DMSEDCUM  | Accumulated net sedimentation flux | (time, LSEDTOT, M, N)|
| TAUKSI, TAUETA | Vector comps; Bottom stress in U,V - point | (time, MC, N) |

## Underlayer properties
| Keyword | Description | Dimensions|
|-----------|-------------|---------|
| MSED         | Mass of sediment in layer | (time, LSEDTOT, nlyr, M, N) |
| LYRFRAC      | Volume fraction of sediment in underlayer | (time, LSEDTOT, nlyr, M, N) |
| DP_BEDLYR    | Vertical position of sediment layer interface | (time, nlyrp1, M, N) |

# Descriptors/grid/coordinates
| Keyword | Description | Dimensions|
|-----------|-------------|---------|
| grid| Attributes describing [SGRID](https://sgrid.github.io/sgrid/) ||
| DPS       | Bottom depth (sigma point) | (time, M, N) |
| NAMCON          | Name of constituent quantity (sediments, solvents(?)) | (LSTSCI) |
| NAMTUR          | Name of turbulent quantities | (LTUR) |
| SIG_LYR         | Sigma coordinates of layer centres| -|
| SIG_INTF        | Sigma coordinates of layer interfaces|-|
| LSTSCI          | Constituents|-|
| LSEDTOT | Array with indices of Sediments | - |
| LSED | Also array with indices of Sediments, no idea what the difference between this and LSEDTOT is  ¯\_(ツ)_/¯ | - |
| KMAXOUT         | User selected output layer interfaces|-|
| KMAXOUT_RESTR   | User selected output layer centres|-|
| GRAVITY         | Gravitational acceleration $\left(\frac{m}{s^2}\right)$ |-|
| RHOCONST | User specified constant density $\left(\frac{kg}{m^3}\right)$ | -|
| time| List of datetimes of outputsteps |time|
| XZ | X Meshgrid |-|
| YZ | Y Meshgrid |-|
| XCOR | X-coordinate of grid points |-|
| YCOR | Y-coordinate of grid points |-|
| M| face dimensions (M:MC (padding: low) |-|
| N| face dimensions (N:NC (padding: low)) |-|
| MC| node dimensions |-|
| NC| node dimensions |-|
| nlyr | Number of underlayer |-|
| nlyrp1 | Interfaces of underlayers |-|
| DP0  | Initial bottom depth (positive down) | (MC, NC) |


## Various
| Keyword | Description |
|-----------|-------------|
|GSQS          | Horizontal area of computational cell |
|DPS0          | Initial bottom depth at sigma points (positive down) |
|DPU0          | Initial bottom depth at u points (positive down) |
|DPV0          | Initial bottom depth at v points (positive down) |
|ALFAS         | Orientation ksi-axis w.r.t. pos.x-axis at water level point |
|PPARTITION    | Partition |
|TAUMAX        | Tau_max in sigma points (scalar |
|UMNLDF        | Filtered U-velocity |
|VMNLDF        | Filtered V-velocity |
|STD_SSUV      | Standard deviation of total suspended transport |
|MORFAC        | morphological acceleration factor (MORFAC) |
|MORFT         | morphological time (days since start of simulation |
|MFTAVG        | morphological time (days since start of simulation) |
|MORAVG        | average MORFAC used during averaging period |

### Stat stuff

These can be toggled in the morphology file under output with `StatVelocity: min, max, mean, and std`

| Keyword | Description |
|-----------|-------------|
|MIN_H1        | Minimum water depth |
|MAX_H1        | Maximum water depth |
|MEAN_H1       | Mean water depth |
|STD_H1        | Standard deviation of water depth |
|MIN_UV        | Minimum velocity |
|MAX_UV        | Maximum velocity |
|MEAN_UV       | mean velocity |
|STD_UV        | Standard deviation of velocity |
|MIN_SBUV      | Minimum total bedload transport |
|MAX_SBUV      | Maximum total bedload transport |
|MEAN_SBUV     | Mean total bedload transport |
|STD_SBUV      | Standard deviation of total bedload transport |
|MIN_SSUV      | Minimum total suspended transport |
|MAX_SSUV      | Maximum total suspended transport |
|MEAN_SSUV     | Mean total suspended transport |

## Masks
| Keyword | Description |
|---------|-------------|
| KCS | Non-active/active water-level point |
| KFU | Non-active/active in U-point |
| KFV | Non-active/active in V-point |
| KCU | Mask array for U-velocity points |
| KCV | Mask array for V-velocity points |


## Others
| Keyword | Description | Dimensions|
|-----------|-------------|---------|
|S1        | Water-level in sigma point|(time, M, N)|
|RTUR1     | Turbulent quantity per layer in sigma point (1. Turbulent Kinetic Energy $k$ and 2. Turbulent energy dissipation $\epsilon$) |(time, LTUR, KMAXOUT, M, N)|
|VICWW     | Vertical eddy viscosity-3D in sigma point|(time, KMAXOUT, M, N)|
|DICWW     | Vertical eddy diffusivity-3D in sigma point|(time, KMAXOUT, M, N)|
|RICH      | Richardson number|(time, KMAXOUT, M, N)|
|VICUV     | horizontal eddy viscosity in sigma point|(time, KMAXOUT_RESTR, M, N)|
|RCA       | Near-bed reference concentration of sediment|(time, LSED, M, N)|
