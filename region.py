
from config import *
from inputbit import InputVector
from column import Column

class Region:
	"""An HTM cortical region"""
	#array of columns or 2D for inhibition
	def __init__(self,rows,cols,inputVector,coverage,desiredLocalActivity):
			self.rows = rows
			self.cols = cols
			self.desiredLocalActivity=desiredLocalActivity
			self.columns = [Column() for i in range(self.rows*self.cols)]	
			self.mapRegionToInputVector(inputVector,coverage)
			self.mapRegionToOutputVector()
			self.inhibitionRadius = min(INITIAL_INHIBITION_RADIUS,self.rows,self.cols)
			self.updateColumnNeighbors()

	def mapRegionToOutputVector(self):
		self.outputVector = InputVector(0)
		for c in self.columns:
			self.outputVector.extendVector(c.getOutputBits())


	def mapRegionToInputVector(self,inputVector,coverage):
		# get the length of the input, and for each input bit assign
		# it to X columns randomly	
		self.inputVector = inputVector
		for bitIndex in range(self.inputVector.getLength()):
				columnIndices = random.sample(range(len(self.columns)),coverage)
				for ci in columnIndices:
					self.columns[ci].mapColumnToInput(inputVector.getBit(bitIndex))

	def getOutputVector(self):
		return self.outputVector


	def convert2Dindex(self,row,col,numCols):
		return row*(numCols) + col

	def computeNeighbors(self,cx,cy,radius):
		neighbors = []
		for dy in range(-radius,radius+1):
			for dx in range(-radius,radius+1):
				# enforce circular shape. optional
				if (dy*dy+dx*dx > radius*radius):
					continue 
				x = cx + dx
				y = cy + dy
				#wrap around: upper boundary check
				x = self.rows + x if (x < 0) else x
				y = self.cols + y if (y < 0) else y
				#wrap around: lower boundary check
				x = x - self.rows if (x >= self.rows) else x
				y = y - self.cols if (y >= self.cols) else y
				index = self.convert2Dindex(x,y,self.cols)
				#if (index < 0 or index >= len(self.columns)):
					#print('radius is' + str(radius))
					#print("bad: " + str(cx) + ", " + str(cy) + ", " + str(x) + ", " + str(y) + ", " + str(dx) + ", " + str(dy))
				n = self.columns[index]
				if (neighbors.count(n) == 0):
					neighbors.append(n)
		return neighbors

	def updateColumnNeighbors(self):
		for i in range(self.rows):
			for j in range(self.cols):
				index = self.convert2Dindex(i,j,self.cols)
				c = self.columns[index]
				c.setNeighbors(self.computeNeighbors(i,j,self.inhibitionRadius))

	def updateInhibitionRadius(self):
		r = 0.0
		for c in self.columns:
			r += c.getNumConnectedProximalSynapses()
		r /= len(self.columns)

		maxRadius = min(self.cols,self.rows)
		r = min(r,maxRadius)
		self.inhibitionRadius = int(r)
		self.updateColumnNeighbors()

	def getAllLearningCells(self,step):
		learningCellList = []
		for c in self.columns:
			learningCells = c.getLearningCells(step)
			learningCellList.extend(learningCells)
		return learningCellList


	def spatialPoolerRun(self):
		[c.updateOverlap() for c in self.columns]
		[c.updateActiveState(self.desiredLocalActivity) for c in self.columns]
		[c.updateBoost() for c in self.columns]
		[c.updateActiveDutyCycle() for c in self.columns]
		self.updateInhibitionRadius()

		#DEBUG THIS
		count = 0
		for c in self.columns:
			if c.active:
				count += 1
		count = 0
		for c in self.columns:
			for cell in c.cells:
				if cell.isActive(CURRENT_TIME_STEP):
					count += 1
		
	def temporalPoolerRun(self):
		[c.advanceTimeStep() for c in self.columns]
		allLearningCells = self.getAllLearningCells(PREVIOUS_TIME_STEP)
		[c.updateCellActivity(allLearningCells) for c in self.columns]
		[c.updateCellPrediction(allLearningCells) for c in self.columns]
		[c.updateCellLearning() for c in self.columns]

	def doRound(self):
		self.spatialPoolerRun()
		self.temporalPoolerRun()
		#record output


