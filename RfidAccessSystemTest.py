import RfidAccessSystem
import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import Reader

#Init 
sql_db = "IITG"
dbTable = "students"
logTable = "logs"
iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidAccessSystem.RfidAccessSystem(sql_db,dbTable,logTable,iq,oq);

#Run waitForCard in separate process.
if __name__ == '__main__':
	p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
	p.start()

while(True):
	try:
		data = oq.get();
		print data;
	except(KeyboardInterrupt, SystemExit):
		print "KeyboardInterrupt in main. Exiting"
		rfas.stopThread();
		break;
