import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import util
import time

continue_reading = True #Boolean that changes to false when sigint is captured.

#Capture SIGINT for cleanup when the script is aborted.
def end_read(signal,frame):
	global continue_reading
	print "Ctrl+C captured, ending read."
	continue_reading = False
	GPIO.cleanup()

#Wait For RFID Card and push UID into a queue
def waitForCard(iq):
	# Hook the SIGINT
	signal.signal(signal.SIGINT, end_read)

	# Create an object of the class MFRC522
	MIFAREReader = MFRC522.MFRC522()

	# Welcome message
	print "Welcome to the MFRC522 data read example"
	print "Press Ctrl-C to stop."

	# This loop keeps checking for chips. If one is near it will get the UID and authenticate
	while continue_reading:
		rfid = None;
		rollno = None;
		data = []; #Raw data read from card.
		uid_old = []; #Used to make sure user doesnt swap cards while reading rollno.
		for i in (6,8,9):       
			#Loop to make sure data is read.
			successful = False;
			while((not successful)and(continue_reading)):
				# Scan for cards    
				(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

				# If a card is found
				# if status == MIFAREReader.MI_OK:
				#   print "Card detected"

				# Get the UID of the card
				(status,uid) = MIFAREReader.MFRC522_Anticoll()

				#Code to check if someone swapped cards while reading roll no.
				#Seriously, throw an exception here.
				if((not uid_old)or(not uid)or(uid_old==uid)):
					if(uid):
						uid_old = uid
				else:
					print "Somebody swapped a card. Throw Exception Here."

				# If we have the UID, continue
				if status == MIFAREReader.MI_OK:

					rfid = util.uid_to_rfid(uid); 

					# This is the default key for authentication
					key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
					
					# Select the scanned tag
					MIFAREReader.MFRC522_SelectTag(uid)

					# Authenticate
					status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, i, key, uid)

					# Check if authenticated
					if status == MIFAREReader.MI_OK:
						data.append(MIFAREReader.MFRC522_Read(i))
						MIFAREReader.MFRC522_StopCrypto1()
						successful = True;
					else:
							print "Authentication error"

		#Get the rollno from the data.
		try:
			temp=[]
			temp.append(data[2][6])
			temp.append(data[2][7])
			temp.append(data[2][8])
			temp.append(data[2][9])
			temp.append(data[1][6])
			temp.append(data[1][7])
			temp.append(data[1][8])
			temp.append(data[1][9])
			temp.append(data[0][6])
			temp2=[]
			for i in temp:
				temp2.append(chr(i))
			rollno = "".join(temp2)
		except IndexError:
			rollno = None;

		if(rollno):
			temp = [];
			temp.append(rfid)
			temp.append(rollno);
			iq.put(temp);
			time.sleep(5);

