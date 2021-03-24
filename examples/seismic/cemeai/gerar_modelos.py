#NBVAL_IGNORE_OUTPUT
import numpy as np
import time
from examples.seismic import Model, plot_velocity

# This class basically represents a layer
class Layer():
	
	# A layer is defined by two "limits" one at the top, one at the bottom
	# currently the layer limits can be either a sine function or a straight line (both defined here by two parameters A and B)
	def __init__(self, velocity, typeTop, paramTopA, paramTopB, typeBottom, paramBottomA, paramBottomB):
		self.velocity = velocity

		self.typeTop = typeTop 
		self.paramTopA = paramTopA
		self.paramTopB = paramTopB

		self.typeBottom = typeBottom
		self.paramBottomA = paramBottomA
		self.paramBottomB = paramBottomB

	def valueTop(self, x):
		if( self.typeTop=='linear' ):
			return self.paramTopA*x + self.paramTopB
		elif( self.typeTop=='sin' ):
			factor = 2.0*np.pi/1000.0 #fixed to 1000 meters (1km)
			return self.paramTopB + self.paramTopA*np.sin( factor*x )

	def valueBottom(self, x):
		if( self.typeBottom=='linear' ):
			return self.paramBottomA*x + self.paramBottomB
		elif( self.typeBottom=='sin' ):
			factor = 2.0*np.pi/1000.0 #fixed to 1000 meters (1km)
			return self.paramBottomB + self.paramBottomA*np.sin( factor*x )


	def applyToGrid(self, v, spacing, origin):

		# Looping over each point for simplicity (instead of vectorising...)
		for i in range(v.shape[0]):
			for j in range(v.shape[1]):
				x = origin[0] + i*spacing[0]
				y = origin[1] + j*spacing[1]

				# Check if this (x,y) point is inside this layer region
				# Dont forget that top and bottom are inverted in this (yTop < yBottom)
				yTop = self.valueTop(x)
				yBottom = self.valueBottom(x)

				# Maybe check the "equals" later on so one layer doesnt override the other...
				if( y>=yTop and y<=yBottom ):
					v[i][j] = self.velocity


def generateRandomModel(shape, spacing, origin, numberOfLayers):

	# Domain limits in meters
	xLimits = ( origin[0], spacing[0]*(shape[0]-1) )
	yLimits = ( origin[1], spacing[1]*(shape[1]-1) )

	# Define a velocity profile. The velocity is in km/s
	v = np.empty(shape, dtype=np.float32)
	v[:, :] = 0.0

	layer = []
	separation = []

	# Initial curve (represents the top of the domain, which is a horizontal line)
	separation.append( ('linear', 0.0, yLimits[0]) )

	# Random "heights" for each curve
	depths = np.random.uniform(0.0, yLimits[1], numberOfLayers-1)
	depths = np.sort(depths)

	# Random velocities (do they need to be sorted?)
	velocities = np.random.uniform(1.5, 3.0, numberOfLayers)
	# velocities = np.sort(velocities)

	# Generating the intermediate curves that separate the layers
	# Currently they can either be sin functions or straight lines
	for i in range(numberOfLayers-1):

		# Choosing randomly between a line or a sin function
		typeCurve = np.random.choice(['linear', 'sin'])

		# Setting random coefficients for the function
		if( typeCurve=='linear' ):
			coefA = np.random.uniform(-0.3, 0.3)
			coefB = depths[i]
		elif( typeCurve=='sin' ):
			coefA = np.random.uniform(50, 150)
			coefB = depths[i]
		else:
			print("Unexpected curve type...\n")

		# Creating the Layer object and applying the velocity to the grid
		separation.append( (typeCurve, coefA, coefB) )
		layer.append( Layer(velocities[i], separation[i][0], separation[i][1], separation[i][2], separation[i+1][0], separation[i+1][1], separation[i+1][2]) )
		layer[i].applyToGrid(v, spacing, origin)

	# Final curve, represents the bottom of the domain (which is a horizontal line)
	i = numberOfLayers-1
	separation.append( ('linear', 0.0, yLimits[1]) )
	layer.append( Layer(velocities[i], separation[i][0], separation[i][1], separation[i][2], separation[i+1][0], separation[i+1][1], separation[i+1][2]) )
	layer[i].applyToGrid(v, spacing, origin)

	# With the velocity and model size defined, we can create the seismic model that
	# encapsulates this properties. We also define the size of the absorbing layer as 10 grid points
	return Model(vp=v, origin=origin, shape=shape, spacing=spacing,
	              space_order=2, nbl=10, bcs="damp")


# Define a physical size
#shape = (101, 101)  # Number of grid point (nx, nz)
#spacing = (10., 10.)  # Grid spacing in m. The domain size is now 1km by 1km
#origin = (0., 0.)  # What is the location of the top left corner. This is necessary to define

# Number of layers for the model
#numberOfLayers = 5

# Seeding the RNG
#np.random.seed(int(time.time()))

# Generates the model
#model = generateRandomModel(shape, spacing, origin, numberOfLayers)

#plot_velocity(model)