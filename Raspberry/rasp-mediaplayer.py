#! /usr/bin/env python

# libraries
import os, sys, subprocess, time, threading

# own modules and packages
import rmconfig, rmmedia, rmutil, rmnetwork
from rmnetwork import udpserver

def shellquote(s):
    return "'" +  s.replace("'", "'\\''") + "'"

def reloadConfig():
	global config
	if rmconfig.configtool.configFileAvailable():
		print "Reading config file..."
		config = rmconfig.configtool.readConfig()

def startMediaPlayer():
	# set config and path for player and start it
	rmmedia.mediaplayer.init(mediaPath)
	media_thread = threading.Thread(target=rmmedia.mediaplayer.play)
	media_thread.daemon = True
	media_thread.start()
	print "Mediaplayer running in thread: ", media_thread.name

def startUdpServer():
	udpserver.start()

# startup image
# subprocess.call(["sudo","fbi","-a", "--once","-noverbose","-T","2", "./raspmedia.jpg"])

config = rmconfig.configtool.initConfig()
reloadConfig()

# default media path
mediaPath = os.getcwd() + '/media/'
print "Media Path: " + mediaPath

startMediaPlayer()
startUdpServer()


# simple CLI to modify and quit program when debugging
time.sleep(0.5)
print ""
print ""
print "Loading CLI....."
time.sleep(0.5)
print ""
print ""
print "Type commands any time -->"
print "-- \"start\" to start the UDP server"
print "-- \"stop\" to stop and close the UDP server"
print "-- \"quit\" to exit the program"

running = True
while running:
    cmd = raw_input("")
    if(cmd == "start"):
        udpserver.start()
    elif(cmd == "stop"):
        udpserver.stop()
    elif(cmd == "quit"):
    	running = False
    else:
    	print "Unknown command: ", cmd

udpserver.stop()
# startup image
# subprocess.call(["sudo","fbi","--once","-a","-noverbose","-T","2", "./raspmedia.jpg"])