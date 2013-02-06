
from config import *
from dendrite import DistalDendriteSegment, SegmentUpdate
from inputbit import InputBit
from synapse import CellSynapse


class Cell:
	"""A cell in a cortical column"""
	def __init__(self):
		self.active = [False for i in range(CELL_ORDER)]
		self.learning = [False for i in range(CELL_ORDER)]
		self.predicted = [False for i in range(CELL_ORDER)]
		#Output of region
		self.output = InputBit()
		self.distal = [DistalDendriteSegment() for i in range(DISTAL_SEGMENTS_PER_COLUMN)]
		self.updates = []

	def isPredicted(self,step):
		return self.predicted[step]

	def isActive(self,step):
		return self.active[step]

	def isLearning(self,step):
		return self.learning[step]

	def setPredicted(self,newPredictedState):
		self.predicted[0] = newPredictedState

	def setActive(self,newActiveState):
		self.active[0] = newActiveState
		self.output.setActive(newActiveState)

	def setLearning(self,newLearningState):
		self.learning[0] = newLearningState

	def addSegment(self,segment):
		self.distal.append(segment)

	def getOutputBit(self):
		return self.output

	def getNumSegments(self):
		return len(self.distal)

	def advanceTimeStep(self):
		self.active.pop()
		self.active.insert(0,False)
		self.predicted.pop()
		self.predicted.insert(0,False)
		self.learning.pop()
		self.learning.insert(0,False)

	def __bestSegment(self,step):
		bestScore = 0
		bestSegment = None
		for segment in self.distal:
			score = segment.overlapRaw(step)
			if (score > bestScore):
				bestScore = score
				bestSegment = segment
		if (bestSegment is not None):
			return (bestSegment,bestScore)
		return (self.__randomSegment(),0)

	def bestSegmentScore(self,step):
		(bestSegment,bestScore) = self.__bestSegment(step)
		return bestScore
	
	def getLearningActiveSegments(self,step):
		activeSegments = []
		for segment in self.distal:
			if segment.isLearningActive(step):
				activeSegments.append(segment)
		return activeSegments

	def getActiveSegments(self,step):
		activeSegments = []
		for segment in self.distal:
			if segment.isActive(step):
				activeSegments.append(segment)
		return activeSegments


	def mostActiveSegment(self,step):
		maxActivity = 0
		maxSegment = None
		for segment in self.getActiveSegments(step):
			overlap = segment.overlap(step)
			if (overlap > maxActivity):
				maxActivity = overlap
				maxSegment = segment
		return maxSegment

	def __randomSegment(self):
		numSegments = len(self.distal)
		index = random.randrange(numSegments)
		return self.distal[index]


	def selectActiveSegment(self,step):
		activeSegments = self.getActiveSegments(step)
		for segment in activeSegments:
			if segment.isSequence():
				return segment

		#No sequence segments, return most active segment
		segment = self.mostActiveSegment(step)
		if (segment is not None):
			return segment

		return self.__randomSegment()


	def activationReport(self):
		if (not self.isPredicted(PREVIOUS_TIME_STEP)):
			return (False, None)
		segment = self.selectActiveSegment(PREVIOUS_TIME_STEP)
		if (not segment.isSequence()):
			return (False,False)
		
		if segment.isLearningActive:
			return (True, True)
		else:
			return (True, False)

		return (False, False)

	def addNewSynapses(self,numNewSynapses,allLearningCells):
		if (numNewSynapses > 0):
			reInsert = False
			if (allLearningCells.count(self) > 0):
				allLearningCells.remove(self)
				reInsert = True
			numLearningCells = len(allLearningCells)
			sampleNum = min(numNewSynapses,numLearningCells)
			sampleIndices = random.sample(xrange(numLearningCells),sampleNum)
			for i in sampleIndices:
				sampledCell = allLearningCells[i]
				activeSegment.CellSynapse(sampledCell)
				
			if (reInsert):
				allLearningCells.append(self)


	def createNewSynapses(self,currentActiveSynapses,allLearningCells):
		numNewSynapses = max(NEW_SYNAPSE_COUNT - len(currentActiveSynapses),0)
		newSynapseList = []
		reInsert = False
		if (allLearningCells.count(self) > 0):
			allLearningCells.remove(self)
			reInsert = True
		numLearningCells = len(allLearningCells)
		sampleNum = min(numNewSynapses,numLearningCells)
		sampleIndices = random.sample(range(numLearningCells),sampleNum)
		for i in sampleIndices:
			sampledCell = allLearningCells[i]
			newSynapseList.append(CellSynapse(sampledCell))
			
		if (reInsert):
			allLearningCells.append(self)

		return newSynapseList

	def generateActivityUpdates(self,createNewSynapses,segmentSequence,allLearningCells,step):

		activeSegment = self.selectActiveSegment(step)
		if (activeSegment is None):
			return
		
		activeSynapses = activeSegment.getActiveSynapses(step)
		newSynapses = None
		if (createNewSynapses):
			newSynapses = self.createNewSynapses(activeSynapses,allLearningCells)
			
		update = SegmentUpdate(activeSegment,activeSynapses,newSynapses,segmentSequence)
		self.updates.append(update)

	def updatePrediction(self,allLearningCells,step):
		for segment in self.distal:
			if segment.isActive(step):
				self.setPredicted(True)
				
				activeSynapses = segment.getActiveSynapses(step)
				activeUpdate = SegmentUpdate(segment,activeSynapses,None,False)
				self.updates.append(activeUpdate)

				(predSegment,_) = self.__bestSegment(step-1)
				predSynapses = predSegment.getActiveSynapses(step-1)
				newSynapses = self.createNewSynapses(predSynapses,allLearningCells)
				predictionUpdate = SegmentUpdate(predSegment,predSynapses,newSynapses,False)

		

	def updateLearning(self,step):
		if self.isLearning(step):
			[update.performUpdate(True) for update in self.updates]
		elif ((not self.isPredicted(step)) and self.isPredicted(step-1)):
				[update.performUpdate(False) for update in self.updates]
		self.updates = []



