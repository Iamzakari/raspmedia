import os, threading
from constants import *
from packages.rmmedia import mediaplayer
from packages.rmconfig import configtool


def interpret(msg_data):
	print "Interpreting incoming data..."

	# initialize with error state
	result = INTERPRETER_ERROR

	data = bytearray(msg_data)
	size, data = readInt(data)
	print "Size: " + str(size)

	flag, data = readShort(data)
	msg = None
	print "Flag: " + str(flag)
	if flag == CONFIG_UPDATE:
		data = readConfigUpdate(data)
		result = INTERPRETER_SUCCESS
	elif flag == PLAYER_START:
		print 'UDP COMMAND Mediaplayer start...'
		mediaplayer.playerState = PLAYER_STARTED
		mediaplayer.play()
		result = INTERPRETER_SUCCESS
	elif flag == PLAYER_STOP:
		print 'UDP COMMAND Mediaplayer stop...'
		mediaplayer.playerState = PLAYER_STOPPED
		mediaplayer.stop()
		result = INTERPRETER_SUCCESS
	elif flag == SERVER_REQUEST:
		data = None
		result = SERVER_REQUEST
	elif flag == FILELIST_REQUEST:
		result = FILELIST_REQUEST
	elif flag == FILELIST_RESPONSE:
		readFileList(data)
		result = FILELIST_REQUEST
	elif flag == CONFIG_REQUEST:
		result = CONFIG_REQUEST
	elif flag == DELETE_FILE:
		numFiles, data = readInt(data)
		files = []
		for i in range(numFiles-1):
			msg, data = readString(data)
			if msg:
				files.append(msg)
		mediaplayer.deleteFiles(files)
	elif flag == PLAYER_IDENTIFY:
		print 'Showing identify image...'
		mediaplayer.identifySelf()
	elif flag == PLAYER_IDENTIFY_DONE:
		print 'Identifying done...'
		mediaplayer.identifyDone()
	elif flag == PLAYER_REBOOT:
		os.system("sudo reboot")

	#print "Remaining data: " + data.decode("utf-8")

	return result, msg

def readFileList(data):
	numFiles, data = readInt(data)
	files = []
	for i in range(numFiles):
		file, data = readString(data)
		if file:
			files.append(file)
	print "FILE LIST READ: ", files

def readConfigUpdate(data):
	print "Current config: ", configtool.config
	print "Processing config update message..."
	key, data = readString(data)
	value, data = readConfigValue(data, key)
	print "New Key/Value Pair:"
	print "KEY: ", key
	print "VALUE: ", value
	configtool.setConfigValue(key, value)
	return data

def readConfigValue(data, key):
	if key == 'image_interval' or key == 'image_enabled' or key == 'video_enabled' or key == 'shuffle' or key == 'repeat' or key == 'autoplay':
		# integer config value
		value, data = readInt(data)
	else:
		# string config value
		value, data = readString(data)
	return value, data

def readInt(data):
	intBytes = data[:4]
	remainingData = data[4:]
	#num = (intBytes[0] << 24) + (intBytes[1] << 16) + (intBytes[2] << 8) + intBytes[3]
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
