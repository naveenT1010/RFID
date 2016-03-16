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
		print 'Go to the following link in your browser: \n' + authorize_url + "\n"
		#Ask for the confirmation code
		code = raw_input('Enter verification code: ').strip()
		#Get the credentials
		credentials = flow.step2_exchange(code)
		#Store the credentials, so that we dont have to do oauth manually from next time.
		storage = Storage(Constants.OAUTH_CREDENTIALS_FILE)
		storage.put(credentials)
		return credentials

## Not using this since we are unable to set the time in Rpi
## If we are able to set ntp in RPi, or if we use a RTC, then we can use this
# def getRecord(sheet_name, credentials, form_filling_time):
# 	record=None
# 	while(record==None):
# 		#Start an app
# 		gc = gspread.authorize(credentials)
# 		#Open a worksheet from spreadsheet with one shot
# 		wks = gc.open(sheet_name).get_worksheet(0)
# 		#Find the record with timestamp after form_filling_time
# 		#Get all the records
# 		all_records = wks.get_all_records()
# 		no_of_records = 0
# 		for i in all_records:
# 			#Compare i['Timestamp'] and form_filling_time
# 			#If i is after form_filling_time, record=i
# 			print "Checking for latest entry. Form filled at " + str(form_filling_time)
# 			if (parser.parse(i['timestamp']) > form_filling_time ) : #If i['Timestamp'] is more recent
# 				record = i;
# 				no_of_records = no_of_records+1
# 				print record['timestamp']
# 		if(no_of_records>1):
# 			print "Error : In main.getRecord, Multiple Entries after form_filling_time"
# 	return record;

def getLatestRecord(sheet_name, credentials):
    record = None
    while(record is None):
        try:
            #Start an app
            gc = gspread.authorize(credentials)
            #Open a worksheet from spreadsheet with one shot
            wks = gc.open(sheet_name).get_worksheet(0)
            #Get all the records
            #This is a performance bug.
            #Records increase over time, and might cause problems.
            all_records = wks.get_all_records()
            record = all_records[-1]
        except:
            print "Exception in gspread.. retrying ..."
            time.sleep(5)
    return record


#Make SIGINT Work
continue_reading = True #Boolean that changes to false when sigint is captured.

#Capture SIGINT for cleanup when the script is aborted.
def end_read(signal,frame):
	global continue_reading
	print "Ctrl+C captured, ending read."
	continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

#Use first command for chrome, second for chromium
#subprocess.Popen(["google-chrome","--kiosk","../user_pages/index.html"])
subprocess.Popen(["chromium-browser","--kiosk","../user_pages/index.html"])
#Start chromix-server. This is crucial for communication between python and chrome.
subprocess.Popen(["chromix-server"])
#Wait some time for chromix-server and kiosk to start.
time.sleep(10)

#Create a mysql db and a mysql cursor
db = MySQLdb.connect(Constants.sql_server,Constants.sql_user,Constants.sql_pass,Constants.sql_db)
cursor = db.cursor()

subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/index.html"])
while (continue_reading):
	#Show the "Welcome" webpage
	print "Please use the RFID Card"

	try:
		data = oq.get(True, Constants.timeOut)
	except Queue.Empty:
		continue

	current_data_dict = {"timestamp":data[0], "rfid":data[1], "rollno":data[2], "name":data[3], "branch":data[4], "hostel":data[5]}

	#Check if this is a new user
	if current_data_dict['rollno'] == None: #If new user
		#Show the registration form to new user
		subprocess.call(["chromix","goto",Constants.REGISTRATION_FORM_URL])

		#Waiting for user to fill the form. When filled this loop will break.
		while not "Response" in str(subprocess.check_output(["chromix","url"])):
			time.sleep(5)
		subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/processing.html"])		

		#Get credentials(using OAuth) for accessing the response sheet
		credentials_for_access = getCredentials(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
		#Get data from the google sheet
		sheet_record = getLatestRecord(Constants.REGISTRATION_RESPONSE_SHEET, credentials_for_access)
		
		#Put rfid data in the sheet dict and remove timestamp from sheet_record
		sheet_record['rfid'] = current_data_dict['rfid']
		del sheet_record['timestamp']
		
		#Put this data into rfid_db in SQL
		rfas.updateDbTable(sheet_record)
		db.commit()
		#Show the "Registration Successful" webpage
		subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/reg_success.html"])		
		print "\nRegister Ho Gya... :D "
		time.sleep(5)
		subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/index.html"])

	else:
		meal = 'B'
		# current_datetime = datetime.datetime.now()
		# #check if the mess is currently working and review can be given now
		# if 8 <= current_datetime.time().hour <= 10:
		# 	meal = 'B'
		# elif 12 <= current_datetime.time().hour <= 14:
		# 	meal = 'L'
		# elif 20 <= current_datetime.time().hour <= 24:
		# 	meal = 'D'
		# else:
		# 	subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/mess_closed.html"])
		# 	break

		#Check for last timestamp of the same rfid
		check_query = "SELECT timestamp FROM mess WHERE rfid = " + str(current_data_dict['rfid']) +' AND meal = "' +meal + '" ORDER BY timestamp DESC LIMIT 1'
		cursor.execute(check_query)
		previous_timestamp = cursor.fetchall()
		print previous_timestamp

		if not ( type(previous_timestamp) == tuple and len(previous_timestamp) == 0 ):
			#Show the "You have already given your review for this meal. Please come back later" webpage
			print "You have already done your review. Please Go Away"
			subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/duplicate_review.html"])	
			time.sleep(5)
			subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/index.html"])

		
		else: #Else, if he is a existing user
			#Show the log form
			subprocess.call(["chromix","goto",Constants.LOG_FORM_URL])

			#Check if he filled the review form
			while not "Response" in str(subprocess.check_output(["chromix","url"])):
				time.sleep(5)
			subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/processing.html"])	
			
			#Get credentials(using OAuth) for accessing the response sheet
			credentials_for_access = getCredentials(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
			
			#Get data from the google sheet
			review_data = getLatestRecord(Constants.LOG_RESPONSE_SHEET,credentials_for_access)
			print review_data
			print "hello"
			#Modify review_data according to needs before updating logtable
			review_data['timestamp'] = current_data_dict['timestamp']
			review_data['rollno'] = current_data_dict['rollno']
			review_data['meal'] = meal
			review_data['rfid'] = current_data_dict['rfid']
			
			#Update the log table
			rfas.updateLogTable(review_data)
			db.commit()
			#Show the "Your review is appreciated" webpage
			subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/log_success.html"])
			print "Your Review has been logged... Do come again.. :)"
			time.sleep(5)
			subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/index.html"])
