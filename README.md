# Delft3D-FLOW Python Tools
### Delft3D-FLOW for humans!

Some sane tools for my thesis too ease the pain of having to work with [Delft3D-FLOW](https://oss.deltares.nl/documents/183920/185723/Delft3D-FLOW_User_Manual.pdf)'s insane file formats and to automate the tedious manual labor involved in setting up multiple succesive simulations.

## JulesD3D

The folder JulesD3D contains some scripts to

* Write or read grid (`.grd`), depth ( `.dep`), enclosure (`.enc`)
* Read and write boundary condition (`.bcc`, `.bct`) files.
* Declaratively generate a  DELFT3D-FLOW4 bathymetry model (depth, grid, enclosure) with a smoothened slope break (DepthModel.py)
* [Prepare subsequent models for restarting from previous simulation](Multirun.md) (multipleruns.py)
* Process netCDF files for plotting with xarray.hvPlot and PyVista

## Notebooks

Furthermore there are some notebooks to

* Visualize [Delft3D-FLOW netCDF output](Delft3D_NetCDF_Output_overview.md)

  * [hvPlot](https://hvplot.pyviz.org/) for interactive plots
  * [Holoviews](http://holoviews.org/) to write cross-section animations to .mp4 files
  * [PyVista](https://www.pyvista.org) for 3D plotting both hydrodynamic and underlayer properties
  * ~~Matplotlib plus some widgets to quickly make some plots~~ [abandoned]
  

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

  * [See this how to visualize Delft3D-Flow with PyVista](Delft3DtoPyVistaApproach.md) 
  
11. Improve code quality and clean notebooks. Less hardcoded variables, more functions

   2. Read up on Python OOP and how to structure packages

## Credits

- Deltares [OpenEarthTools](https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/) (abandoned)
- spmls' [Pydelft](https://github.com/spmls/pydelft) 
- NOAA's [Gridded](https://github.com/NOAA-ORR-ERD/gridded)
- [PyVista](https://www.pyvista.org)
