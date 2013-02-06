
from region import Region
from config import *
from inputbit import InputVector

def testCount():
	rows = 5
	cols = 5
	coverage = 20
	numbits = 10
	numRounds = 500
	trainingRounds = numRounds/4
	originalInputVector = InputVector(numbits)
	inputVector = InputVector(0)

	pred = dict()
	#repeat several times to increase activity:
	for i in range(3):
		inputVector.extendVector(originalInputVector)

	desiredLocalActivity = DESIRED_LOCAL_ACTIVITY

	r = Region(rows,cols,inputVector,coverage,desiredLocalActivity)
	outputVector = r.getOutputVector()
	correctBitPredctions = 0
	for round in range(numRounds):
		#print("Round: " + str(round))
		# if (round % 2 == 0):
		# 	val = 682
		# else:
		# 	val = 341
		val = round % 30
		setInput(originalInputVector,val)
		inputString = inputVector.toString()
		outputString = outputVector.toString()
		# for bit in inputVector.getVector():
		# 	printBit(bit)
		# print('')
		# print(inputString)


		if outputString in pred:
			curPredString = pred[outputString]
		else:
			curPredString = "[New input]"
		pred[outputString] = inputString

		printStats(inputString,curPredString)
		if (round > trainingRounds):
			correctBitPredctions += stringOverlap(curPredString,pred[outputString])
				 

		r.doRound()
		printColumnStats(r)
	for key in pred:
		print("key: " + key + " pred: " + pred[key])

	print("Accuracy: " + str(float(correctBitPredctions)/float((30*(numRounds-trainingRounds)))))


def stringOverlap(str1,str2):
	count = 0
	length = min(len(str1),len(str2))
	for i in range(length):
		if (str1[i] == str2[i]):
			count += 1
	return count


def printStats(inputVector,outputVector):
	print('Input-: ',end='')
	print(inputVector)
	print('Output: ',end='')
	print(outputVector)


def setInput(inputVector,bitArray):
	for i in range(inputVector.getLength()):
		bitValue = (bitArray & (1 << i) > 0)
		inputVector.getBit(i).setActive(bitValue)


def printColumnStats(r):
	alarmColumnCount = 0
	stableColumnCount = 0
	errorColumnsFound = 0
	for c in r.columns:
		if (not c.isActive()):
				continue
		allCellsActive = True
		cellActiveFound = False
		for cell in c.cells:
			if (not cell.isActive(CURRENT_TIME_STEP)):
				allCellsActive = False
			else:
				cellActiveFound = True
		if allCellsActive:
			alarmColumnCount += 1
		elif cellActiveFound:
			stableColumnCount += 1
		else:
			errorColumnsFound += 1
	print("Alarm Columns: " + str(alarmColumnCount) + " Stable Columns: " + str(stableColumnCount))


