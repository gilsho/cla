
from config import *

class Synapse:
	"""A synaptic connection"""
	def __init__(self):
		self.weight = 0
		self.permanence = PERMANENCE_THRESHOLD*(1 + (random.random()-0.5)/10)

	def increasePermanence(self):
		self.permanence += PERMANENCE_INC
		self.permanence = min(self.permanence,1)

	def decreasePermanence(self):
		self.permanence -= PERMANENCE_DEC
		self.permanence = max(self.permanence,0)

	def connected(self):
		return (self.permanence > PERMANENCE_THRESHOLD)


class ProximalSynapse(Synapse):
	"""A synaptic connection to an input bit"""
	def __init__(self,inputBit):
		Synapse.__init__(self)
		self.inputBit = inputBit

	def isActive(self):
		return self.connected() and self.inputBit.isActive()

	def isActiveRaw(self):
		return self.inputBit.isActive()


class CellSynapse(Synapse):
	"""A synaptic connection to a cell in a cortical column"""
	def __init__(self,inputCell):
		Synapse.__init__(self)
		self.inputCell = inputCell

	def isActive(self,step):
		return self.connected() and self.inputCell.isActive(step)

	def isActiveRaw(self,step):
		return self.inputCell.isActive(step)

	def isLearning(self,step):
		return self.inputCell.isLearning(step)





