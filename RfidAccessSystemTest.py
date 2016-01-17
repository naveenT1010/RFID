import RfidAccessSystem
import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import Reader
import Constants

#Init 
iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidAccessSystem.RfidAccessSystem(Constants.sql_db,Constants.dbTable,Constants.logTable,iq,oq);

#Run waitForCard in separate process.
if __name__ == '__main__':
	p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
	p.start()

while(True):
	try:
		data = oq.get();
		print data
		if(data[2] is None):
			temp = {'rfid':data[1],'name':'Rishabh','rollno':'I dont know'}
			rfas.updateDbTable(temp)
	except(KeyboardInterrupt, SystemExit):
		print "KeyboardInterrupt in main. Exiting"
		rfas.stopThread();
		break;
