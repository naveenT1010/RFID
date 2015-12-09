import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import util

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
            iq.put(rfid);

            #TEST CODE
            print "Card detected.";