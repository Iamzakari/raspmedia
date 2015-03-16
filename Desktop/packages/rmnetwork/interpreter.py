import threading
from constants import *


def interpret(msg_data):
	# print "Interpreting incoming data..."

	# initialize with error state
	result = INTERPRETER_ERROR

	data = bytearray(msg_data)
	size, data = readInt(data)
	# print "Size: " + str(size)

	flag, data = readShort(data)
	result = flag
	returnData = None
	# print "Flag: " + str(flag)
	if flag == SERVER_REQUEST_ACKNOWLEDGE:
		result = INTERPRETER_SERVER_REQUEST
		devType, data = readInt(data)
		devFlag, data = readInt(data)
		devName, data = readString(data)
		devSpace, data = readInt(data)
		# print "DEVICE FOUND: ", devName
		# print "Type: %d - Flag: %d" % (devType, devFlag)
		returnData = (devName, devType, devFlag, devSpace)
	elif flag == FILELIST_REQUEST:
		result = INTERPRETER_FILELIST_REQUEST
	elif flag == FILELIST_RESPONSE:
		returnData = readFileList(data)
		result = INTERPRETER_FILELIST_REQUEST
	elif flag == CONFIG_REQUEST or flag == GROUP_CONFIG_REQUEST:
		result = flag
		returnData = readConfigData(data)
	elif flag == PLAYER_UPDATE_ERROR:
		result = flag
		returnData, data = readString(data)

	#print "Remaining data: " + data.decode("utf-8")

	return result, returnData

def readConfigData(data):
	config, data = readString(data)
	return config

def readFileList(data):
	numFiles, data = readInt(data)
	# print "Reading received file list of size ", numFiles
	files = []
	for i in range(numFiles):
		file, data = readString(data)
		if file:
			files.append(file.decode('utf-8'))
	# print "Filelist read: ", files
	return files

def readInt(data):
	intBytes = data[:4]
	remainingData = data[4:]
	# LE change
	num = (intBytes[3] << 24) + (intBytes[2] << 16) + (intBytes[1] << 8) + intBytes[0]
	return num, remainingData

def readShort(data):
	intBytes = data[:2]
	remainingData = data[2:]
	#num = (intBytes[0] << 8) + intBytes[1]
	# LE change
	num = (intBytes[1] << 8) + intBytes[0]
	return num, remainingData

def readString(data):
	size, data = readInt(data)
	strBytes = data[:size]
	remainingData = data[size:]
	inStr = str(strBytes)
	return inStr, remainingData
