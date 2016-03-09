import RfidSystem
import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import Reader
import Constants

#Init 
iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidSystem.RfidSystem(Constants.sql_db,Constants.dbTable,Constants.logTable,iq,oq);

#Run waitForCard in separate process.
if __name__ == '__main__':
	p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
	p.start()

while(True):
	try:
		#Print the result
		data = oq.get();
		print data

		# #TEST CODE
		# print type(data)
		# print [type(i) for i in data]


		# #Test updateDbTable
		# if(data[2] is None):
		# 	temp = {'rfid':data[1],  'name':'Rishabh',  'rollno':'130121028'}
		# 	rfas.updateDbTable(temp)

		#Test updateLogTable
		logdata = {'timestamp':data[0], 'rfid':data[1],  'name':data[2],  'rollno':'130102051'}
		rfas.updateLogTable(logdata)

	except(KeyboardInterrupt, SystemExit):
		print "KeyboardInterrupt in main. Exiting"
		rfas.stopThread();
		break;
