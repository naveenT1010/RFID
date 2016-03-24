import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import util
import time
import datetime
import Constants
import threading

class Reader(object):
	def __init__(self,iq):
		self.continue_reading = True #Bool that changes to false when sigint is captured.
		self.pause_reading = False #Bool that decides if reading is paused

		#Start waitForCard in a new thread.
		t=threading.Thread(target=self.waitForCard, args=(iq,));
		t.start();

	#Function that sets running to false and stops the thread.
	def stopThread(self):
		self.continue_reading = False;

	#Function that pauses the thread.
	def pause_read(self):
		self.pause_reading = True;

	#Fuction that resumes the thread.
	def resume_read(self):
		self.pause_reading = False;


	#Wait For RFID Card and push UID into a queue
	def waitForCard(self,iq):
		# Create an object of the class MFRC522
		MIFAREReader = MFRC522.MFRC522()

		# Welcome message
		print "Welcome to the MFRC522 RFID System"
		print "Press Ctrl-C to stop."

		# This loop keeps checking for chips. If one is near it will get the UID and authenticate
		while self.continue_reading:
			if(self.pause_reading):
				pass
			else:
				# Scan for cards    
				(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

				# If a card is found
				#if status == MIFAREReader.MI_OK:
					#print "Card detected"

				# Get the UID of the card
				(status,uid) = MIFAREReader.MFRC522_Anticoll()

				# If we have the UID, continue
				if status == MIFAREReader.MI_OK:
					#Push the UID into a queue
					rfid = util.uid_to_rfid(uid); 
					temp = [];
					temp.append(rfid);
					temp.append(datetime.datetime.now());
					iq.put(temp);
					#If we put a card in the queue, wait for 5 seconds.
					#This is to avoid sending the same card several times.
					time.sleep(Constants.timeSleep);

					#TEST CODE
					print "Card detected.";
					print temp