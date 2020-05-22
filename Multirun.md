## Multirun scripts

* Auto-generate multiple Delft3D-FLOW files  for multiple subsequent (restarting) simulations

  * Master Defenition File (.mdf)

    * Adds `Restid='identifier'+ run_nr`, get's the identifier from the .mdf filename
    * Change smoothing time to zero `Tlfsmo = 0.0000000e+000`
    * Change times of restart and history files:

    `Flmap = T_start output_time_step(remains the same) T_end`

    `Flhis = T_start output_time_step(remains the same) T_end`

    * Due to a bug in Delft3D-FLOW, NetCDF cannot restart a map file from a specific time. Therefore, the index of the output step must be used. This is restart time step is calculated automatically and added with `Restid_timeindex` keyword and value. This is the only way to restart from a netCDF map file!

  * Morphology .mor file

    * Resets morphological smoothing time `MorStt  = 0`

  * .bcc, .bct, .sed files

    * Adds duration of one simulation to all time steps