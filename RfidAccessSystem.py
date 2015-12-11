import MySQLdb
import threading
import multiprocessing

class RfidAccessSystem(object):
	def __init__(self, dbName, tableName, iq, oq):
		print "INIT OF RfidAccessSystem."
		self.dbName = dbName;
		self.tableName = tableName;
		self.db  = MySQLdb.connect('localhost','pi','raspberry', dbName);
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
			if(not self.iq.empty()):
				#Handle Exceptions here
				# rfid = self.iq.get();
				temp = self.iq.get();
				rfid = temp[0];
				rollno = temp[1];
				query = "SELECT * FROM "+ self.tableName +" WHERE RFID= "+ str(rfid);
				
				##TEST CODE
				# print "In RfidAccessSystem:getRowFromDB, RFID : ", rfid;
				# print "In RfidAccessSystem:getRowFromDB, RollNo : ", rollno;

				#Handle Exceptions here
				self.cur.execute(query);
				data = self.cur.fetchall();
				
				#Handle Exceptions here
				self.oq.put(data);

				if(not data):
					query = "INSERT INTO " + self.tableName + " ( rfid , rollno ) " + " VALUES (" + str(rfid) + "," + "'" +rollno + "'"+ ")"
					self.cur.execute(query);
					self.db.commit();
					print query;



			

