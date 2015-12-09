import RfidAccessSystem
import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import Reader

#Init 
dbName = "IITG";
tableName = "students";
iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidAccessSystem.RfidAccessSystem(dbName,tableName,iq,oq);

#Run waitForCard in separate process.
if __name__ == '__main__':
	p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
	p.start()

print "Getting Data from oq in main"
while(True):
	try:
		print "Getting Data from oq : ",oq.get();
	except(KeyboardInterrupt, SystemExit):
		print "KeyboardInterrupt in main. Exiting"
		rfas.stopThread();
		break;
