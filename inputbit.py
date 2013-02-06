
from config import *

class InputBit:
	"""A single input bit to the cortical region"""
	def __init__(self):
		self.bit = False

	def setActive(self,newActiveState):
		self.bit = newActiveState

	def isActive(self):
		return self.bit

class InputVector:
	"""A complete set of input bits to the cortical region"""
	def __init__(self,length):
		self.vector = [InputBit() for i in range(length)]

	def getLength(self):
		return len(self.vector)

	def getBit(self,index):
		return self.vector[index]

	def getVector(self):
		return self.vector

	def appendBit(self,inputBit):
		self.vector.append(inputBit)

	def extendVector(self,inputVector):
		self.vector.extend(inputVector.getVector())

	def toString(self):
		string = ""
		for bit in self.vector:
			if (bit.isActive()):
				string = string + "1"
			else:
				string = string + "0"
		return string
