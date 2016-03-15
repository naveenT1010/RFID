import time
import MySQLdb
import datetime
import subprocess
import RfidSystem
import multiprocessing
import RPi.GPIO as GPIO
import MFRC522
import signal
import Reader
import Constants
import os
import Queue
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import httplib2
import pprint
import gspread
from dateutil import parser

#Init 
iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidSystem.RfidSystem(Constants.sql_db,Constants.dbTable,Constants.logTable,iq,oq);

#Run waitForCard in separate process.
if __name__ == '__main__':
	p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
	p.start()

#function for checking or getting the authentication for response sheet access
def getCredentials(OAUTH_CLIENT_ID,OAUTH_CLIENT_SECRET,OAUTH_SCOPE,OAUTH_REDIRECT_URI):
	# Run through the OAuth flow and retrieve credentials
	if(os.path.isfile(Constants.OAUTH_CREDENTIALS_FILE)): #If stored credentials is present
		#Get the stored credentials
		storage = Storage(Constants.OAUTH_CREDENTIALS_FILE)
		credentials = storage.get()
		#Refresh the credentials
		http = httplib2.Http()
		http = credentials.authorize(http)
		credentials.refresh(http)
		return credentials

	else: #If stored credentials is not present. This will occur only once.
		#Create a flow
		flow = OAuth2WebServerFlow(OAUTH_CLIENT_ID,OAUTH_CLIENT_SECRET,OAUTH_SCOPE,OAUTH_REDIRECT_URI)
		#Get a url to follow for authentication
		authorize_url = flow.step1_get_authorize_url()
		print 'Go to the following link in your browser: ' + authorize_url + "\n"
		#Ask for the confirmation code
		code = raw_input('Enter verification code: ').strip()
		#Get the credentials
		credentials = flow.step2_exchange(code)
		#Store the credentials, so that we dont have to do oauth manually from next time.
		storage = Storage(Constants.OAUTH_CREDENTIALS_FILE)
		storage.put(credentials)
		return credentials

def getRecord(sheet_name, credentials, form_filling_time):
	record=None
	while(record==None):
		#Start an app
		gc = gspread.authorize(credentials)
		#Open a worksheet from spreadsheet with one shot
		wks = gc.open(sheet_name).get_worksheet(0)
		#Find the record with timestamp after form_filling_time
		#Get all the records
		all_records = wks.get_all_records()

		no_of_records = 0
		for i in all_records:
			#Compare i['Timestamp'] and form_filling_time
			#If i is after form_filling_time, record=i
			print "Checking for latest entry. Form filled at " + str(form_filling_time)
			if (parser.parse(i['timestamp']) > form_filling_time ) : #If i['Timestamp'] is more recent
				record = i;
				no_of_records = no_of_records+1
				print record['timestamp']
		if(no_of_records>1):
			print "Error : In main.getRecord, Multiple Entries after form_filling_time"

	return record;

def getLatestRecord(sheet_name, credentials):	
	time.sleep(5)
	#Start an app
	gc = gspread.authorize(credentials)
	#Open a worksheet from spreadsheet with one shot
	wks = gc.open(sheet_name).get_worksheet(0)
	#Find the record with timestamp after form_filling_time
	#Get all the records
	all_records = wks.get_all_records()
	print "\nThe last record is : " + str(all_records[-1])
	return all_records[-1];

#for google chrome, use first command and for chromium, use the successor
# subprocess.Popen(["google-chrome","--kiosk","../user_pages/index.html"])
# subprocess.Popen(["chromium-browser","--kiosk","../user_pages/index.html"])
subprocess.Popen(["chromix-server"])
time.sleep(5)

db = MySQLdb.connect(Constants.sql_server,Constants.sql_user,Constants.sql_pass,Constants.sql_db)
# db = MySQLdb.connect('localhost','pi','raspberry','rfid')
cursor = db.cursor()

while (True):
	meal = None
	print "Please use the RFID Card"

	try:
		data = oq.get(True, Constants.timeOut)
	except Queue.Empty:
		continue

	current_data_dict = {"timestamp":data[0], "rfid":data[1], "rollno":data[2], "name":data[3], "branch":data[4], "hostel":data[5]}
	#check if this is a new User
	#for new user, entries other than rfid is empty
	if current_data_dict['rollno'] == None:
		#show the registration form to new user
		subprocess.call(["chromix","goto",Constants.REGISTRATION_FORM_URL])

		#waiting for user to fill the form. when filled this loop will break.
		while not "Response" in str(subprocess.check_output(["chromix","url"])):
			time.sleep(1)
		#check time when the form is filled
		form_submission_time = datetime.datetime.now()

		#get credentials for accessing the response sheet
		credentials_for_access = getCredentials(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
		#get data from the excel and put in the logtable
		sheet_record = getLatestRecord(Constants.REGISTRATION_RESPONSE_SHEET, credentials_for_access)
		#put rfid data in the sheet dict and remove timestamp from sheet_record
		sheet_record['rfid'] = current_data_dict['rfid']
		del sheet_record['timestamp']
		#put this data into rfid_db in SQL
		rfas.updateDbTable(sheet_record)
		print "\nRegister Ho Gya... :D ... Go Away"

	else:
		current_datetime = datetime.datetime.now()
		#check if the mess is currently working and review can be given now
		if 8 <= current_datetime.time().hour <= 10:
			meal = 'B'
		elif 12 <= current_datetime.time().hour <= 14:
			meal = 'L'
		elif 20 <= current_datetime.time().hour <= 24:
			meal = 'D'
		else:
			print "You cant give review at this time. Go Away.."
			break

		#check for last timestamp of the same rfid
		check_query = "SELECT timestamp FROM mess WHERE rfid = " + str(current_data_dict['rfid']) +' AND meal = "' +meal + '" ORDER BY timestamp DESC LIMIT 1'
		cursor.execute(check_query)
		previous_timestamp = cursor.fetchall()
		print previous_timestamp

		if not ( type(previous_timestamp) == tuple and len(previous_timestamp) == 0 ):
			#He has already given review for this meal. 
			print "You have already done your review. Please Go Away"
		
		else:
			print "in line 157"
			#show the review form
			subprocess.call(["chromix","goto",Constants.LOG_FORM_URL])
			#check if he filled the review form
			while not "Response" in str(subprocess.check_output(["chromix","url"])):
				time.sleep(1)
			
			credentials_for_access = getCredentials(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
			review_data = getLatestRecord(Constants.LOG_RESPONSE_SHEET,credentials_for_access)
			review_data['timestamp'] = current_data_dict['timestamp']
			review_data['rollno'] = current_data_dict['rollno']
			review_data['meal'] = meal
			review_data['rfid'] = current_data_dict['rfid']
			
			# #update the log table
			rfas.updateLogTable(review_data)
			print "Your Review has been logged... Do come again.. :)"





#-----JUNK BELOW-------

# def open_kiosk():
# 	try:
# 		subprocess.check_output(["google-chrome","--kiosk","index.html"])
# 	except subprocess.CalledProcessError:
# 		print "Couldnt open Chrome in kiosk mode"

# def responder():
# 	try:
# 		subprocess.check_output(["google-chrome","--kiosk","http://fb.com"])
# 	except subprocess.CalledProcessError:
# 		print "Could Load 2nd Tab"

# def main():
# 	# thread.start_new_thread(open_kiosk,())
# 	# time.sleep(5)
# 	thread.start_new_thread(responder,())
# 	# subprocess.call(["google-chrome","--kiosk","http://facebook.com"])


# # import commands
# # commands.getoutput("google-chrome --kiosk 'http://google.com' ")
# # time.sleep(3)
# # commands.getoutput("google-chrome --kiosk 'http://fb.com' ")

# if __name__ == '__main__':
# 	main()

