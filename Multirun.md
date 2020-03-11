## Multirun scripts

* Auto-generate multiple Delft3D-FLOW files  for multiple subsequent (restarting) simulations

  * Master Defenition File (.mdf)

    * Adds `Restid='identifier'+ run_nr`, get's the identifier from the .mdf filename
    * Change smoothing time to zero `Tlfsmo = 0.0000000e+000`
    * Change times of restart and history files:

    `Flmap = TStart output_time_step(remains the same) Tend`

    `Flhis = TStart output_time_step(remains the same) Tend`

    * Calculates restart time step and add `Restid_timeindex` keyword and value, this is the only way to restart from a netCDF map file

  * Morphology .mor file

    * Resets morphological smoothing time `MorStt  = 0`

  * .bcc, .bct, .sed files

    * Adds duration of one simulation to all time steps