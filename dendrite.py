
from config import *
from synapse import *

class Dendrite:
	"""A dendrite segment"""
	def __init__(self):
		self.synapses = []
		

class ProximalDendrite(Dendrite):
	"A dendrite consisting of synaptic connection to input bits"
	def __init__(self):
		Dendrite.__init__(self)
		self.synapses = []

	def listen(self,inputBit):
		self.synapses.append(ProximalSynapse(inputBit))

	def increasePermanences(self):
		for s in self.synapses:
			s.increasePermanence(0.01*PERMANENCE_THRESHOLD)

	def updatePermanences(self):
		for s in self.synapses:
			if s.isActive(): 
				s.increasePermanence()
			else:
				s.decreasePermanence()

	def overlap(self,boost):
		overlapBits = 0
		for synapse in self.synapses:
			if synapse.isActive():
				overlapBits += 1
		if (overlapBits < MIN_OVERLAP):
			overlapBits = 0
		return overlapBits*boost

	def getNumConnectedSynapses(self):
		count = 0
		for s in self.synapses:
			if s.connected():
				count += 1
		return count


class DistalDendriteSegment(Dendrite):
	"A dendrite consisting of synaptic connection to other cortical columns"
	def __init__(self):
		Dendrite.__init__(self)
		#this defers from original algorithm
		self.sequence = True

	def listen(self,inputCell):
		self.synapses.append(CellSynapse(inputCell))

	def isActive(self,step):
		return (self.overlapActive(step) > DISTAL_ACTIVATION_THRESHOLD)

	def isLearningActive(self,step):
		return (self.overlapLearning(step) > DISTAL_ACTIVATION_THRESHOLD)

	def isSequence(self):
		return self.sequence

	# Breaks abstraction. limit use of function
	def getActiveSynapses(self,step):
		activeSynapses = []
		for synapse in self.synapses:
			if synapse.isActive(step):
				activeSynapses.append(synapse)
		return activeSynapses

	def getSynapses(self):
		return self.synapses
	#

	def addSynapses(self,newSynapses):
		if newSynapses is not None:
			self.synapses.extend(newSynapses)

	def setSequence(self,newSequenceState):
		self.sequence = newSequenceState

	def overlapActive(self,step):
		overlap = 0
		for synapse in self.synapses:
			if synapse.isActive(step):
				overlap += 1
		if (overlap < MIN_OVERLAP):
			overlap = 0
		return overlap	

	def overlapRaw(self,step):
		overlapRaw = 0
		for synapse in self.synapses:
			if synapse.isActiveRaw(step):
				overlapRaw += 1
		if (overlapRaw < MIN_OVERLAP):
			overlapRaw = 0
		return overlapRaw

	def overlapLearning(self,step):
		overlapLearning = 0
		for synapse in self.synapses:
			if synapse.isLearning(step):
				overlapLearning += 1
		return overlapLearning


class SegmentUpdate():
	def __init__(self,segment,activeSynapses,newSynapses,isSequence):
		self.activeSegment = segment
		self.activeSynapses = activeSynapses
		self.isSequence = isSequence
		self.newSynapses = newSynapses


	def performPositiveReinforcement(self):
		for synapse in self.activeSegment.getSynapses():
			if (self.activeSynapses.count(synapse) > 0):
				synapse.increasePermanence()
			else:
				synapse.decreasePermanence()

	def performNegativeReinforcement(self):
		for synapse in self.activeSynapses:
			synapse.decreasePermanence()


	def performUpdate(self,positiveReinforcement):
		#if self.isSequence:
		#	self.activeSegment.setSequence(True)

		#this defers from original algorithm
		self.activeSegment.setSequence(True)

		if positiveReinforcement:
			self.performPositiveReinforcement()
		else:
			self.performNegativeReinforcement()
		
		self.activeSegment.addSynapses(self.newSynapses)
