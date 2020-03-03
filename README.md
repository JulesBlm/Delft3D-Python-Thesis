# Delft3D-Flow Python Tools

Some sane tools for my thesis too ease the pain of having to work with Delft3D-FLOW's insane file formats.

The folder JulesD3D contains some tools
* To write or read grid (`.grd`), depth ( `.dep`), enclosure (`.enc`)
* Read and write boundary condition (`.bcc`, `.bct`) files.
* A script to generate DELFT3D-FLOW4 depth files with a smoothened slope break
* A script that prepares subsequent models for restarting from previous simulation (multipleruns.py). 

Furthermore there are some notebooks to

* Visualize [Delft3D-FLOW netCDF output](Delft3D_NetCDF_Output_overview.md)

  * [hvPlot](https://hvplot.pyviz.org/) for interactive plots
  * [Holoviews](http://holoviews.org/) to write cross-section animations to .mp4 files
  * [PyVista](https://www.pyvista.org) for 3D plotting both hydrodynamic and underlayer properties
  * Matplotlib plus some widgets to quickly make some plots [abandoned]
  
  
## Multirun script
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

  * 


### Disclaimer

This is very much a work in progress so it's all still very messy and hacky:  ¯\_(ツ)_/¯.  I use this to visualise the results of modelling turbidity currents in Delft3D. If you're looking for tools to visualize Delft3D ocean or river modelling I'd suggest to look at one of these libraries

* [Geoviews](http://geoviews.org/)
* [xrviz](https://xrviz.readthedocs.io/en/latest/)
* [Gridded](https://github.com/NOAA-ORR-ERD/gridded)
* [Thyme](https://github.com/noaa-ocs-modeling/thyme) 
* [xgcm](https://github.com/xgcm/xgcm)
* [Iris](https://scitools.org.uk/iris/docs/latest/)
* [gridgeo](https://pyoceans.github.io/gridgeo/gridgeo_tour.html)

## Potential To Do list

2. Use Panel for better & cleaner widgets, both for hvPlot and for PyVista
  
3. Properly structure JulesD3D folder as package

4. Use ufuncs to increase performance

5. Move notebooks to separate folders

6. ~~Plot according to grid. Delft3D uses a staggered grid and an equidistant sigma ocean grid for depth.~~ **DONE**

   - ~~Plot vertical cross-section on true bathymetry ie scale sigma layers to their thickness~~
   - Better vertical coordinates ( [Maybe use this](https://github.com/jbusecke/xarrayutils/blob/master/doc/vertical_coords.ipynb) )
   - Make holoviews animation of side cross-section, doesn't work right now/very slow
   - Check location of values on staggered grid (face vs edge etc) maybe use parts of gridded

7. ~~Get Holoviews write to animation file working~~

8. ~~Use DataShader to speed up plotting with HoloViews/hvPlot~~

9. ~~Bottom animations with true bathymetry with PyVista~~

10. ~~3D volumes with [PyVista](https://docs.pyvista.org/)~~

   * ~~Old approach: Voxilize point cloud~~ (Abandoned because a grid is much nicer to work with and more true to the model)

   * Right now the approach is like this
     
      1. The X and Y meshgrids in the NetCDF file are repeated Nr of sigma interfaces/layers times
      ```python
         x_interfaces = np.repeat(trim.XCOR.values[:,:, np.newaxis], trim.SIG_INTF.size, axis=2)
         y_interfaces = np.repeat(trim.YCOR.values[:,:, np.newaxis], trim.SIG_INTF.size, axis=2)
      ```
         Now all three have equal dimensions (62, 202, 81)
      
      2. Next we flatten/ravel these arrays, now we have three arrays of size 62 * 202 * 81= 1 014 444
      
      3. With column stack we get an array with x,y,z coordinates, (1014444, 3) this we can plot as point cloud
      
      ```python
   		xyz_interfaces = np.column_stack((x_interface_ravel, 				y_interface_ravel, depth_ravel))
   		xyz_interfaces.shape
   	```
      4. Then define a StructuredGrid and add these as its points
   	```python
   depth_interfaces_grid = pv.StructuredGrid()
   depth_interfaces_grid.points = xyz_interfaces
     ```

   	5. Then set the dimensions of the StructuredGrid so PyVista/VTK can 'reconstruct' the quad cells of the mesh. According to this issue in the PyVista repo ( [Visualise a 2D image from array of x, y, z and data points](https://github.com/pyvista/pyvista-support/issues/28#issuecomment-514016207) ) this works because the nodes are in the right order.
      ```python
      depth_interfaces_grid.dimensions = [81, 202, 62] 
      ```

   	As it says in [the docs](https://docs.pyvista.org/core/index.html#core-api)
   	
   	> - A [`pyvista.StructuredGrid`](https://docs.pyvista.org/core/point-grids.html#pyvista.StructuredGrid) is a regular lattice of points aligned with an internal coordinate axes such that the connectivity can be **defined by a grid ordering**. These are commonly made from `np.meshgrid()`. The cell types of structured grids must be 2D Quads or 3D Hexahedrons. 
   	
   	And now we have a StructuredGrid true to the sigma-layer model (ie depth) with (in this case) 980880 cells and 1 014 444 points!
   	
   	

11. Improve code quality and clean notebooks. Less hardcoded variables, more functions
   2. Read up on Python OOP and how to structure packages

## Credits

- Deltares [OpenEarthTools](https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/) (abandoned)
- spmls' [Pydelft](https://github.com/spmls/pydelft) 
- NOAA's [Gridded](https://github.com/NOAA-ORR-ERD/gridded)
- [PyVista](https://www.pyvista.org)
