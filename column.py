
from config import *
from cell import Cell
from dendrite import ProximalDendrite
from inputbit import InputBit, InputVector


class Column:
	"""A column in an HTM cortical region"""
	def __init__(self):
		self.proximal = ProximalDendrite();
		self.cells = [Cell() for i in range(CELLS_PER_COLUMN)]
		self.neighbors = []
		self.overlap = 0
		self.active = False
		self.activeDutyCycle = 0
		self.overlapDutyCycle = 0
		self.boost = 1
		self.scheduledUpdates = None

	def setNeighbors(self,neighbors):
		self.neighbors = neighbors

	def mapColumnToInput(self,inputBit):
		self.proximal.listen(inputBit)

	def getOverlap(self):
		return self.overlap

	def getActiveDutyCycle(self):
		return self.activeDutyCycle

	def getOutputBits(self):
		outputBits = InputVector(0)
		for cell in self.cells:
			outputBits.appendBit(cell.getOutputBit())
		return outputBits

	def getLearningCells(self,step):
		learningCells = []
		for cell in self.cells:
			if cell.isLearning(step):
				learningCells.append(cell)
		return learningCells

	def getNumConnectedProximalSynapses(self):
		return self.proximal.getNumConnectedSynapses()

	def isActive(self):
		return self.active

	def updateOverlap(self):
		self.overlap = self.proximal.overlap(self.boost)	

	def calculateMinLocalActivity(self,desiredLocalActivity):
		neighborOverlap = []
		for c in self.neighbors:
			neighborOverlap.append(c.getOverlap())
		neighborOverlap.sort()
		if desiredLocalActivity < len(neighborOverlap):
			minLocalActivity = neighborOverlap[desiredLocalActivity]
		else:
			minLocalActivity = 0

		return minLocalActivity

	def calculateMinDutyCycle(self):
		maxDutyCycle = 0
		for c in self.neighbors:
			maxDutyCycle = max(maxDutyCycle,c.getActiveDutyCycle())
		return 0.01 * maxDutyCycle

	def updateActiveState(self,desiredLocalActivity):
		#Set active state taking into account inhibition
		minLocalActivity = self.calculateMinLocalActivity(desiredLocalActivity)		
		if (self.overlap > 0 and self.overlap > minLocalActivity):
			self.active = True
			self.proximal.updatePermanences()
		else:
			self.active = False

	def updateParameters(self):
		minDutyCycle = self.calculateMinDutyCycle()
		self.updateActiveDutyCycle()
		self.updateBoost(minLocalActivity)
		self.updateOverlapDutyCycle(minLocalActivity)

	def updateActiveDutyCycle(self):
		activity = 1 if (self.active) else 0
		self.activeDutyCycle = DECAY_RATE*self.activeDutyCycle + (1-DECAY_RATE)*activity

	def updateOverlapDutyCycle(self,minDutyCycle):
		self.overlapDutyCycle = DECAY_RATE*self.overlapDutyCycle + (1-DECAY_RATE)*self.overlap
		if (self.overlapDutyCycle < minDutyCycle):
			self.proximal.increasePermanences()

	def updateBoost(self):
		minDutyCycle = self.calculateMinDutyCycle()
		if (self.activeDutyCycle < minDutyCycle):
			self.boost += BOOST_INCREMENT

	def bestSegmentScoreCell(self,step):
		bestSegmentScore = 0
		bestCell = None
		for cell in self.cells:
			score = cell.bestSegmentScore(step)
			if (score > bestSegmentScore):
				bestSegmentScore = score
				bestCell = cell
		return bestCell

	def bestSegmentCountCell(self):
		minSegmentCount = self.cells[0].getNumSegments()
		bestCell = self.cells[0]
		for cell in self.cells:
			segmentCount = cell.getNumSegments()
			if (segmentCount < minSegmentCount):
				minSegmentCount = segmentCount
				bestCell = cell
		return bestCell

#BestMatchingCell(c)
# For the given column, return the cell with the best matching segment (as 
# defined above). If no cell has a matching segment, then return the cell with 
# the fewest number of segments.

	def bestMatchingCell(self,step):
		cell = self.bestSegmentScoreCell(step)
		if (cell is None):
			cell = self.bestSegmentCountCell()
		return cell
		

	def advanceTimeStep(self):
		for cell in self.cells:
			cell.advanceTimeStep()

	def updateCellActivity(self,allLearningCells):
		for cell in self.cells:
			cell.setActive(False)

		if (not self.active):
			return

		buPredicted = False
		lcChosen = False
		for cell in self.cells:
			(cellPredicted,cellLearning) = cell.activationReport()
			if (cellPredicted):
				buPredicted = True
				cell.setActive(True)
				if (cellLearning):
					cell.setLearning(True)
					lcChosen = True
		
		if (not buPredicted):
			for cell in self.cells:
				cell.setActive(True)

		if (not lcChosen):
			learningCell = self.bestMatchingCell(PREVIOUS_TIME_STEP)
			learningCell.setLearning(True)
			learningCell.generateActivityUpdates(True,True,allLearningCells,PREVIOUS_TIME_STEP)

	def updateCellPrediction(self,allPrevLearningCells):
		for cell in self.cells:
			cell.updatePrediction(allPrevLearningCells,CURRENT_TIME_STEP)

	def updateCellLearning(self):
		for cell in self.cells:
			cell.updateLearning(CURRENT_TIME_STEP)



