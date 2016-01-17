import MySQLdb
import threading
import multiprocessing
import datetime
import Queue
import Constants

class RfidAccessSystem(object):
	def __init__(self, sql_db, dbTable, logTable, iq, oq):
		print "INIT OF RfidAccessSystem."
		self.sql_db = sql_db #The sql database name
		self.dbTable = dbTable #Table that stores the users of the system
		self.logTable = logTable #Table that stores logs
		self.db  = MySQLdb.connect('localhost','pi','raspberry', self.sql_db);
		self.cur = self.db.cursor();
		self.iq  = iq;
		self.oq  = oq;
		#Below thread will run as long as this is true. User will set this to false to stop the thread.
		self.running = True; 
		
		#Start getRowFromDB in a new thread. 
		#It will keep running as long the object of this class is alive, and so, 
		#NEEDS TO RUN IN A SEPARATE THREAD
		t=threading.Thread(target=self.getRowFromDB);
		t.start();

	#Function that sets running to false and stops the thread.
	def stopThread(self):
		self.running = False;

	def getRowFromDB(self):
		while(self.running):
			#Get the data from the q
			try:
				temp = self.iq.get(True, Constants.timeOut)
			except Queue.Empty:
				continue
			rfid = temp[0]
			timestamp = temp[1]

			#Try to get the row from dbTable
			select_query = "SELECT * FROM "+ self.dbTable +" WHERE RFID= "+ str(rfid);
			self.cur.execute(select_query)
			data = self.cur.fetchall()

			#Handle the various cases
			if(len(data)>1): #RFID is not UNIQUE in dbTable
				#Throw rfid not unique exception
				print "Duplicate RFID in dbTable"
			elif(len(data)==1): #We got exactly one row from dbTable
				#Return the row to application
				data = list(data[0]); #Convert from tuple to list
				data.insert(0,timestamp); #Add the timestamp to the data
			else: #The card is new
				#Create an entry in db with rfid
				insert_query = "INSERT INTO " + self.dbTable + " (rfid) VALUES " + "(" + str(rfid) + ")"
				self.cur.execute(insert_query)
				self.db.commit();
				#Select this entry
				select_query = "SELECT * FROM "+ self.dbTable +" WHERE RFID= "+ str(rfid);
				self.cur.execute(select_query)
				data = self.cur.fetchall()
				#Add timestamp
				data = list(data[0]); #Convert from tuple to list
				data.insert(0,timestamp); #Add the timestamp to the data
				
			#Send it to application
			#Put the data into the output q
			self.oq.put(data);

			#Update the Log Table with the timestamp and rfid
			insert_query = "INSERT INTO " + self.logTable + " (timestamp, rfid) VALUES " + "(" + "'" +timestamp.strftime("%Y-%m-%d %H:%M:%S") + "'" + "," + str(rfid) + ")"
			self.cur.execute(insert_query)
			self.db.commit()

	def updateDbTable(self,data):
		rfid = data['rfid']
		del data['rfid']

		#SQL UPDATE STATEMENT GENERIC SYNTAX
		#UPDATE table_name
		#SET column1=value1,column2=value2,...
		#WHERE some_column=some_value;

		update_query = "UPDATE " + self.dbTable + " SET "
		temp = [str(i[0])+"="+"'"+str(i[1])+"'" for i in list(data.iteritems())]
		update_query = update_query + ",".join(temp)
		update_query = update_query + " WHERE rfid=" + str(rfid)

		#Cant use the same db and cursor objects as getRowFromDB
		#Probably because its running in a separate thread
		tempdb = MySQLdb.connect('localhost','pi','raspberry', self.sql_db)
		tempcur = tempdb.cursor()
		tempcur.execute(update_query)
		tempdb.commit()

	#Need to add this
	# def updateLogTable():


