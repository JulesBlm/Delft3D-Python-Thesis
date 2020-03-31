# Delft3D-FLOW Python Tools for humans
### Declarative Delft3D-FLOW file generation and visualisation

Some sane tools for my thesis too ease the pain of having to work with [Delft3D-FLOW](https://oss.deltares.nl/documents/183920/185723/Delft3D-FLOW_User_Manual.pdf)'s insane file formats and to automate the tedious manual labor involved in setting up multiple succesive simulations.

## JulesD3D

The folder JulesD3D contains some scripts to

* Write or read grid (`.grd`), depth ( `.dep`), enclosure (`.enc`)
* Read and write boundary condition (`.bcc`, `.bct`) files.
* Declaratively generate a  DELFT3D-FLOW4 bathymetry model (depth, grid, enclosure) with a smoothened slope break (DepthModel.py)
* [Prepare subsequent models for restarting from previous simulation](Multirun.md) (multipleruns.py)
* Process netCDF files for plotting with xarray.hvPlot and PyVista
* [See this on how to visualize Delft3D-Flow netCDF with PyVista](Delft3D_to_PyVista_Approach.md) 

## Notebooks

Furthermore there are some notebooks to

* Visualize [Delft3D-FLOW netCDF output](Delft3D_NetCDF_Output_overview.md)

  * [hvPlot](https://hvplot.pyviz.org/) for interactive plots
  * [Holoviews](http://holoviews.org/) to write cross-section animations to .mp4 files
  * [PyVista](https://www.pyvista.org) for 3D plotting both hydrodynamic and underlayer properties
  * ~~Matplotlib plus some widgets to quickly make some plots~~ [abandoned]
  

##  Demo images

<img width="700px" title="Silt concentration 3D sideview" src="output_material/example_silt_conc_sideview_yz.png" />

<img src="output_material/depth_sans_enc.png" title="Model Bathymetry z-axis scaled by 25" width="700px" />

<img src="output_material/example_underlayers.png" title="Model Bathymetry z-axis scaled by 25" width="700px" />

See the folder 'output_material' for more images and videos.

### Disclaimer

This is very much a work in progress so it's all still very messy and hacky:  ¯\_(ツ)_/¯.  I use this to visualise the results of modelling turbidity currents and their deposits in Delft3D. If you're looking for tools to visualize Delft3D ocean or river modelling I'd suggest to look at one of these libraries.

* [Geoviews](http://geoviews.org/)
* [xrviz](https://xrviz.readthedocs.io/en/latest/)
* [Gridded](https://github.com/NOAA-ORR-ERD/gridded)
* [Thyme](https://github.com/noaa-ocs-modeling/thyme) 
* [xgcm](https://github.com/xgcm/xgcm)
* [Iris](https://scitools.org.uk/iris/docs/latest/)
* [gridgeo](https://pyoceans.github.io/gridgeo/gridgeo_tour.html)

## Potential To Do list

1. Script for reading writing Morphology files
2. Notebook showing overview of MDF file
2. Use Panel for better & cleaner widgets, both for hvPlot and for PyVista
3. Properly structure JulesD3D folder as package
4. Use ufuncs to increase performance
5. Move notebooks to separate folders
6. ~~Plot according to grid. Delft3D uses a staggered grid and an equidistant sigma ocean grid for depth.~~ 
   - ~~Plot vertical cross-section on true bathymetry ie scale sigma layers to their thickness~~
   - Better vertical coordinates for Holoviews ( [Maybe use this](https://github.com/jbusecke/xarrayutils/blob/master/doc/vertical_coords.ipynb) )doesn't work right now/extremely slow in hvPlot
   - Check location of values on staggered grid (face vs edge etc) maybe use parts of Gridded for this
8. Improve code quality and clean notebooks. Less hardcoded variables, more functions
  * Read up on Python OOP/classes

## Credits

- Deltares [OpenEarthTools](https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/) (abandoned)
- spmls' [Pydelft](https://github.com/spmls/pydelft) 
- NOAA's [Gridded](https://github.com/NOAA-ORR-ERD/gridded)
- [PyVista](https://www.pyvista.org)
