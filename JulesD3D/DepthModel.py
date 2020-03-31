# It's a giant mess but it does the job, my job
# TODO
# * Not sure if this is how to Class in Python  ¯\_(ツ)_/¯
# * Make better use of Depth and Grid classes
# * Fix bank_index (center) mess!
# * Make nice n clear repr string
# * Smoothen slope break direction independent

from JulesD3D.dep import Depth
from JulesD3D.grid import Grid
from JulesD3D.enc import Enclosure
# from JulesD3D.bnd import Boundaries
import bezier
import numpy as np
import math, os
from mpl_toolkits.mplot3d import Axes3D
import cmocean.cm as cmo
import matplotlib.pyplot as plt
import traceback
import pprint
pp = pprint.PrettyPrinter(indent=4)

class DepthModel(object):
    def __init__(self, **kwargs):
        self.filenames = kwargs.get("filenames", {})
        self.grid = kwargs.get("grid", {})
        self.channel = kwargs.get("channel", {})
        self.bathymetry = kwargs.get("bathymetry", {})
                
    def __repr__(self):
        string = f'''
        Making grid and depth files with these properties
        Filenames: {pp.pprint(self.filenames)}
        Grid: {pp.pprint(self.grid)}
        Channel: {pp.pprint(self.channel)}
        Bathymetry: {pp.pprint(self.bathymetry)}
        '''
        # keys = [*filenames.keys()]
        # vals = [*filenames.values()]
        # list(zip(keys, vals))
        
        return string
        
    @staticmethod
    def slopeFunction(slope_radians, length):
        return math.tan(slope_radians) * length        
    
    # TODO: Why don't i use the Grid class the generate the meshgrid?
    def makeNewGrid(self):
        """Makes uniform rectilinear grid with numpy meshgrid"""
        print("------ Making new Delft3D grid ------")
        print("x_gridstep", self.grid['x_gridstep'])
        print("y_gridstep", self.grid['y_gridstep'])
        print("width", self.grid['width'])
        print("length", self.grid['length'])
        
        if self.grid['width'] % self.grid['x_gridstep']:
            raise Exception("Width is not a multiple of x_gridstep")
        if self.grid['length'] % self.grid['y_gridstep']:        
            raise Exception("Length is not a multiple of y_gridstep")
            
        x_gridstep = self.grid['x_gridstep']
        y_gridstep = self.grid['y_gridstep']

        xList = np.array([i for i in range(0, self.grid['width'] + x_gridstep, x_gridstep)])
        yList = np.array([i for i in range(0, self.grid['length'] + y_gridstep, y_gridstep)]) + 100 # + 100 is default start y in REFGRID

        xDim, yDim = [len(xList), len(yList)]
        print(f"MNKmax = {xDim + 1} {yDim + 1} SIGMALAYERS")
        
        print("xDim", xDim)
        print("yDim", yDim)
        
        self.grid['dims'].append([xDim, yDim])
        
        x_grid, y_grid = np.meshgrid(xList, yList)
        self.grid['x_grid'] = x_grid
        self.grid['y_grid'] = y_grid
        self.grid['shape'] = (xDim, yDim)
        
    def writeDepFile(self):
        new_depth = Depth()
        new_depth.values = self.bathymetry['depth']
        new_depth.shape = self.bathymetry['depth'].shape
        print("Writing depth file to:", self.filenames['dep'])

        try:
            Depth.write(new_depth, self.filenames['dep'])
        except IOError
            print("\t TypeError: Could not write .dep file!")
            traceback.print_exc()            
        except TypeError:
            print("\t TypeError: Could not write .dep file!")
            traceback.print_exc()
        except RuntimeError: 
            print("\t RuntimeError: Could not write .dep file!")
            traceback.print_exc()
        except NameError:
            print("\t NameError: Could not write .dep file!")
            traceback.print_exc()

        
    def writeGridFile(self):
        print("Writing grid file with shape", self.grid['shape'])
        if 'x_grid' not in self.grid:
            raise Exception("Run makeNewGrid before calling this function")
        
        newGrid = Grid()
        newGrid.x = self.grid['x_grid']
        newGrid.y = self.grid['y_grid']
        newGrid.shape = self.grid['shape']
        newGrid.properties = {'Coordinate System': 'Cartesian', 'xori': 0.0, 'yori': 0.0, 'alfori': 0.0}
        Grid.write(newGrid, self.filenames['grid'])
        
    @staticmethod
    def smoothenBreak(cross_section, break_point_index, smoothen_over):
        '''
        Smoothen slope break with bezier curve
        TODO: Make direction independent
        '''
        x_cross_section, depth_cross_section = cross_section
        
        # Smooth with bezier curve between these points
        start_smooth_index, end_smooth_index = [break_point_index - smoothen_over,\
                                                break_point_index + smoothen_over]

        # Prepare section to be smoothed for Bezier
        nodes_x = np.array(x_cross_section[start_smooth_index:end_smooth_index])
        nodes_y = np.array(depth_cross_section[start_smooth_index:end_smooth_index])
        
        # print(len(nodes_x), len(nodes_y))
        
        # fig_q, ax_q = plt.subplots()
        # fig_q.suptitle('Bathymetry cross-sections (Unsmoothened!)')
        # ax_q.plot(range(start_smooth_index, end_smooth_index), -nodes_y)
        # ax_q.set_xlabel('N (grid number)')
        # ax_q.set_ylabel('Depth [m]')
        # ax_q.grid()
        
        # Feed nodes into bezier instance
        nodes = np.array([nodes_x, nodes_y])
#         curved = bezier.Curve(nodes, degree=3)
        curved = bezier.Curve.from_nodes(nodes)

        # Get new depth (y-values) from bezier instance
        s_vals_channel = np.linspace(0.0, 1.0, 2 * smoothen_over)
        smoothened_channel_part = curved.evaluate_multi(s_vals_channel)[1]
#         y_cross_section[start_smooth:end_smooth] = curved.evaluate_multi(s_vals_channel)[1]
        
        smooth_cross_section = depth_cross_section.copy()
        smooth_cross_section[start_smooth_index:end_smooth_index] = smoothened_channel_part
#         test_depth_smooth = smoothened_channel_part[-1]
#         test_depth_unsmooth = depth_cross_section[end_smooth_index]
#         difference = test_depth_unsmooth - test_depth_smooth
#         print("Difference", test_depth_unsmooth - test_depth_smooth)
    
        return np.array(smooth_cross_section) # smoothened cross section
    

    def generateBathymetrySlopeBreak(self):
        '''
        Generate depth matrix with one slope break at steep channel and
        less steep basin smoothen with a bézier curve
        Assumes slope break is at channel end
        Bezier: https://pomax.github.io/bezierinfo/
        '''
        print('------ Making bathymetry ------')
        print('* Minimum depth: ', self.bathymetry['initial_depth'])
        print('* Channel slope: ', self.channel['slope'])
        print('* Basin slope: \t', self.bathymetry['slope'])

        # Fill grid ones
        xDim, yDim = self.grid['shape']
        depth_matrix = np.zeros((xDim+1, yDim+1))

        # express channel length in y gridsteps
        channel_length_index = int((self.channel['length'])/self.grid['y_gridstep']) + 1
        print("channel_length_index", channel_length_index)
        
        steep_slope_radians = math.radians(self.channel['slope'])
        # Make list containing channel depths according to supplied slope
        steep_slope_range = range(0, self.channel['length'] + self.grid['y_gridstep'], self.grid['y_gridstep'])
        # [0, 300, 600, ..., 15000]

        # channel slope depths
        steep_slope_list = np.array([self.slopeFunction(steep_slope_radians, i) for i in steep_slope_range])
        # example (m): [  0.0, 6.546, 13.092, ..., 314.209, 320.755, 327.301]
#         print("steep_slope_list.shape", steep_slope_list.shape)
        
        steep_slope_last_depth = steep_slope_list[-1] + self.channel['depth']

        # Make list containing basin depths according to supplied slope
        basin_slope_radians = math.radians(self.bathymetry['slope'])
        basin_length = self.grid['length'] - self.channel['length'] + self.grid['y_gridstep'] # One gridstep because mesh is one larger
                
        basin_list_range = range(0, basin_length, self.grid['y_gridstep'])
        basin_list = np.array([self.slopeFunction(basin_slope_radians, i) for i in basin_list_range]) + steep_slope_last_depth
#         print("basin_list.shape", basin_list.shape)

        combined_slopes_list = np.concatenate((steep_slope_list, basin_list), axis=0) + self.bathymetry['initial_depth']
        channel_list = combined_slopes_list.copy()

#         print("combined_slopes_list.shape", combined_slopes_list.shape)
        
        y_grid_section = self.grid['y_grid'][:,0]
        
        # Smoothen non-channel slope break
        normal_cross_section = [y_grid_section, combined_slopes_list] # x, y values for smoothening
        smoothened_model_list = self.smoothenBreak(normal_cross_section, channel_length_index, 10)
        
#         print("smoothened_model_list", smoothened_model_list)
            
        # Add NON-CHANNEL slopes to depth matrix
        depth_matrix_with_slopes = depth_matrix.copy()
        depth_matrix_with_slopes = depth_matrix_with_slopes + smoothened_model_list
    
        # Add channel depth
        channel_list[0:channel_length_index] += self.channel['depth']
        
#         print("Channel list", channel_list)
  
        channel_cross_section = [y_grid_section, channel_list] # x, y values for smoothening
        smoothened_channel_list = self.smoothenBreak(channel_cross_section, channel_length_index, 10)

#         print("smoothened_channel_list", smoothened_channel_list)
    
        depth_matrix_with_channel = depth_matrix_with_slopes.copy()
        
        # Add channel slope to depth grid
        channel_grid_cells = int(self.channel['width']/self.grid['x_gridstep']) + 1#2
        print("channel_grid_cells", channel_grid_cells)
        bank_width = (self.grid['width'] - self.channel['width'])/2
        print('* bank_width', bank_width)
        bank_index = int((bank_width/self.grid['x_gridstep']))
        print('* bank_index', bank_index)
        channel = np.tile(smoothened_channel_list, (channel_grid_cells, 1))

#         print("channel", channel)        
        
        xDim, yDim = self.grid['shape']
        
        bank_left = bank_index
        bank_right = bank_index + channel_grid_cells

        # TODO MOVE TO BOTTOM
        depth_matrix_with_channel[:,-1] = np.nan # set last row to nan
        depth_matrix_with_channel[-1] = np.nan # set last column to nan

        print("bank_left", bank_left)
        print("bank_right", bank_right)
        print('\ndepth_matrix[bank_left:bank_right,:] shape', depth_matrix_with_channel[bank_left:bank_right,:].shape)
        print('channel', channel.shape)
        depth_matrix_with_channel[bank_left:bank_right,:] = channel
        
        self.bathymetry['depth'] = depth_matrix_with_channel.T
        
        print("--- Writing enclosure file ---")
        print("xDim: ", xDim)
        print("yDim: ", yDim)
        enclosure_options = dict(
            dims = (xDim, yDim),
            filename=self.filenames['enc'],
            bank_left=bank_left, bank_right=bank_right+2,
            channel_length_index=channel_length_index-1
        )
        
        enc = Enclosure(**enclosure_options)
        enclosureX, enclosureY = enc.write()
    
        return depth_matrix_with_channel.T
    
    @staticmethod
    def makeModelAtOnce(self):
        '''
        Performs all the generation steps and writing files at once in the right order
        '''
        self.makeNewGrid()
        self.writeGridFile()
        self.generateBathymetrySlopeBreak()
        self.writeDepFile()
    
    def plotCrossSection(self):
        
        y_section = self.grid['y_grid'][:,0] 
        cross_section = self.bathymetry['depth'][:,1]
        cross_section_channel = self.bathymetry['depth'][:,30]

        fig1, (ax1, ax2, ax3) = plt.subplots(1,3)
        fig1.suptitle('Smoothened bathymetry cross-sections')

        ax1.plot(y_section, -cross_section[:-1],
                 y_section, -cross_section_channel[:-1])
        ax1.legend(['Normal', 'Channel'], loc='best')

        ax1.set(xlabel='N [m]', ylabel='Depth [m]', title='Complete cross-section ')
        ax1.tick_params(labelrotation=45)
        ax1.grid()
        
#         ax2.plot(y_section[40:60], -cross_section[40:60],
#                  y_section[40:60], -cross_section_channel[40:60]  )
#         ax2.plot(y_section[48:54], -cross_section[48:54],
#                  y_section[48:54], -cross_section_channel[48:54]  )
        ax2.plot(range(40,60), -cross_section[40:60],
                 range(40,60), -cross_section_channel[40:60] )    
    
        ax2.legend(['Normal', 'Channel'], loc='best')

        ax2.set(xlabel='N [m]', ylabel='Depth [m]', title='Zoom on channel')
        ax2.grid()
        
#         ax3.plot(y_section[51:71], -cross_section[51:71],
#                  y_section[51:71], -cross_section_channel[51:71])
        ax3.plot(range(51,71), -cross_section[51:71],
                 range(51,71), -cross_section_channel[51:71])

        ax3.legend(['Normal', 'Channel'], loc='best')

        ax3.set(xlabel='N [m]', ylabel='Depth [m]', title='Zoom on basin section')
        ax3.tick_params(labelrotation=45)
        ax3.grid()

        
    def plot3D(self):
        Z = self.bathymetry['depth'][0:-1,0:-1] #new_depth.values[0:-1,0:-1]
        print("x shape:", self.grid['shape'][0])
        print("y shape:", self.grid['shape'][1])
        print("z shape:", Z.shape)

        fig_3d = plt.figure(figsize=(7.5,5))
        ax_3d = fig_3d.gca(projection='3d')

        surface = ax_3d.plot_surface(self.grid['x_grid'], self.grid['y_grid'], Z, cmap=cmo.deep, label='Initial Bathymetry')
        fig_3d.colorbar(surface, shrink=0.5, aspect=5)
        ax_3d.set_xlabel('X [m]')
        ax_3d.set_ylabel('Y [m]')
        ax_3d.set_zlabel('Depth [m]')
        ax_3d.view_init(40,90)

        ax_3d.set_zlim(np.amax(Z), 300)
        plt.show()
        
    def plotGrid(self):
        ''' Plot flipped grid'''
        gridFig, gridAx = plt.subplots()
        gridAx.plot(self.grid['y_grid'].transpose(), self.grid['x_grid'].transpose(), 'gray')
        gridAx.plot(self.grid['y_grid'], self.grid['x_grid'], 'gray')
        gridAx.set_xlabel('n [m]')
        gridAx.set_ylabel('m [m]')
        gridAx.set_aspect('equal')
        
    def plotDepthAndGrid(self):
        fig, [gridAx0, gridAx1] = plt.subplots(1,2)

        Z = self.bathymetry['depth'][0:-1,0:-1] #new_depth.values[0:-1,0:-1]
        min_depth, max_depth = [self.bathymetry['initial_depth'], Z.max()]

        gridAx0.set_aspect('equal')
        gridAx0.set_title('In grid numbers')
#         gridAx0.plot(self.grid['x_grid'].transpose(), self.grid['y_grid'].transpose(),\
#                      self.grid['x_grid'], self.grid['y_grid'], 'gray', linewidth=0.25, alpha=0.5)
        grid_im = gridAx0.pcolor(Z, vmin=min_depth, vmax=max_depth, cmap=cmo.deep)        
        gridAx0.set_xlabel('m')
        gridAx0.set_ylabel('n')
#         gridAx0.grid(linewidth=0.5, alpha=0.8, color='w')# xdata=newGrid.x[0][1:-1], ydata=newGrid.y[0][1:-1])

        gridAx1.set_aspect('equal')
        gridAx1.pcolor(self.grid['x_grid'], self.grid['y_grid'], Z,  vmin=min_depth, vmax=max_depth, cmap=cmo.deep)
        gridAx1.set_title('In meters')
        gridAx1.set_xlabel('x [m]')
        gridAx1.set_ylabel('y [m]')
        gridAx1.grid(linewidth=0.5, alpha=0.8, color='w')# xdata=newGrid.x[0][1:-1], ydata=newGrid.y[0][1:-1])
        fig.colorbar(grid_im, ax=gridAx1)

        # gridAx2.set_aspect('equal')
        # gridAx2.contourf(newGrid.x, newGrid.y, view_bathy[0:-1,0:-1])#  vmin=min_depth, vmax=max_depth, cmap=cmo.deep)
        # gridAx2.set_title('Contour just because')
        # gridAx2.set_xlabel('x [m]')
        # gridAx2.set_ylabel('y [m]')
        # gridAx2.grid(linewidth=0.5, alpha=0.8, color='w')# xdata=newGrid.x[0][1:-1], ydata=newGrid.y[0][1:-1])

        # gridAx0.plot(enclosureX, enclosureY, c='#ffb9be', linewidth=3)        