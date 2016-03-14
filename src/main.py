#The main function of the rfid system.
#This basically opens google forms when a new id comes.
#Allows updating of database and log tables using the data from the response sheets.

#For opening google forms, we use webbrowser module of python.
import webbrowser
#Import Modules need for OAuth2 Authentication
import httplib2
import pprint
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage  
import os
#Import github.com/burnash/gspread which is an api to access google sheets.
#Google doesn't have sheets api for python
#It suggests that we use sheets from app scripts and use appscripts api, but fuck that.
import gspread
#RfidSystem,Reader and MFRC522 are the RFID Modules
import RfidSystem
import Reader
import MFRC522
#This module contains all App-Level Constants
import Constants
#RPi.GPIO is python module for running GPIO pins of RPi
import RPi.GPIO as GPIO
#dateutil.parser is used to parse date from google sheet. dateutil is much more flexible than datetime
from dateutil import parser
#We need datetime for datetime.datetime.now()
import datetime
#Multiprocessing and Signal and python modules
import multiprocessing
import signal


# def getNewestRecordFromSheet(sheet_uri):
#     # Run through the OAuth flow and retrieve credentials
#     if(os.path.isfile(Constants.OAUTH_CREDENTIALS_FILE)): #If stored credentials is present
#         #Get the stored credentials
#         storage = Storage(Constants.OAUTH_CREDENTIALS_FILE)
#         credentials = storage.get()
#         #Refresh the credentials
#         http = httplib2.Http()
#         http = credentials.authorize(http)
#         credentials.refresh(http)
#     else: #If stored credentials is not present. This will occur only once.
#         #Create a flow
#         flow = OAuth2WebServerFlow(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
#         #Get a url to follow for authentication
#         authorize_url = flow.step1_get_authorize_url()
#         print 'Go to the following link in your browser: ' + authorize_url + "\n"
#         #Ask for the confirmation code
#         code = raw_input('Enter verification code: ').strip()
#         #Get the credentials
#         credentials = flow.step2_exchange(code)
#         #Store the credentials, so that we dont have to do oauth manually from next time.
#         storage = Storage(Constants.OAUTH_CREDENTIALS_FILE)
#         storage.put(credentials)

#     #Start an app
#     gc = gspread.authorize(credentials)

#     # Open a worksheet from spreadsheet with one shot
#     wks = gc.open(sheet_uri).sheet1

#     #Get all the records
#     all_records = wks.get_all_records()

#     #Find the record with newest timestamp
#     newest_record = None
#     for i in all_records:
#         #Compare i['Timestamp'] and newest_record['Timestamp']
#         #If i is newer than newest_record, update newest_record=i
#         i['Timestamp'] 

#     return newest_record;





def getRecordFromSheet(sheet_uri, form_display_time):
    # Run through the OAuth flow and retrieve credentials
    if(os.path.isfile(Constants.OAUTH_CREDENTIALS_FILE)): #If stored credentials is present
        #Get the stored credentials
        storage = Storage(Constants.OAUTH_CREDENTIALS_FILE)
        credentials = storage.get()
        #Refresh the credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)
    else: #If stored credentials is not present. This will occur only once.
        #Create a flow
        flow = OAuth2WebServerFlow(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
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

    #Start an app
    gc = gspread.authorize(credentials)

    # Open a worksheet from spreadsheet with one shot
    wks = gc.open(sheet_uri).sheet1

    #Get all the records
    all_records = wks.get_all_records()

    #Find the record with timestamp after form_display_time
    record=None
    while(record==None):
        no_of_records = 0
        for i in all_records:
            #Compare i['Timestamp'] and form_display_time
            #If i is after form_display_time, record=i
            if (parser.parse(i['Timestamp'] > form_display_time ) : #If i['Timestamp'] is more recent
                record = i;
                no_of_records = no_of_records+1

    if(no_of_records>1)
        print "Error : In main.getRecordFromSheet, Multiple Entries after form_display_time"

    return record;






# Flow :
# Create and RFID system
# Read Entries from the output queue
# If Person is new : 
#     Open the Registration Form using webbrowser.open, and Tell him to fill it.
#         This form is the only communication point with the end-user, so it should have all necessary details
#         such as, what he should do after filling, should he contact the admin of the system for access privileges etc.
#     Pull the response into python using oauth2+gspread
#     Use the data to create a new entry in mysql table : rfid_database
# Else If Person is existing : 
#     Open the Log Form using webbrowser.open, and Tell him to fill it.
#         Again, this form is the only point of communication, and should contain all details.
#         NOTE : If the specific system needs no log form, the log form url can be left empty.
#     Pull the response into python using oauth2+gspread
#     Use the data to create a new entry in mysql table : rfid_logs



#Init
iq = multiprocessing.Queue(); #Queue that links Reader.waitForCard and RfidSystem.RfidSystem
oq = multiprocessing.Queue(); #Queue that links RfidSystem.RfidSystem and main.py(current module)
rfid_system = RfidSystem.RfidSystem(Constants.sql_db,Constants.dbTable,Constants.logTable,iq,oq);

#Run waitForCard in separate process.
#The __name__ == __main__ check makes sure that we dont get into a infinite loop of creating processes. Dont ask me more, I know its stupid, but thats how python works. 
if __name__ == '__main__':
    p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
    p.start()

#Wait for data in oq,
while(True):
    #The try catch is for breaking out of the loop if user stops it with ctrl-c
    try:
        data = oq.get();
        # # TEST CODE
        # print data
        # print type(data)
        # print [type(i) for i in data]

        #data will be of this format :timestamp,rfid,rollno,...
        #If the user is a new user, rollno will be None or ""
        #So we can check for this and open the REGISTRATION_FORM
        if((data[2] is None)or(data[2]=="")): #If user is a new user
            
            form_display_time = datetime.datetime.now()
            webbrowser.open(Constants.REGISTRATION_FORM_URI) #Open the form
            

            # response_received = False
            # while(not response_received):
                # newest_record = getNewestRecordFromSheet(Constants.REGISTRATION_RESPONSES_URI)
            record = getRecordFromSheet(Constants.REGISTRATION_RESPONSES_URI, form_display_time)







        # #Test updateDbTable
        # if(data[2] is None):
        #   temp = {'rfid':data[1],  'name':'Rishabh',  'rollno':'130121028'}
        #   rfid_system.updateDbTable(temp)

        #Test updateLogTable
        logdata = {'timestamp':data[0], 'rfid':data[1],  'name':data[2],  'rollno':'130102051'}
        rfid_system.updateLogTable(logdata)

    except(KeyboardInterrupt, SystemExit):
        print "KeyboardInterrupt in main. Exiting"
        rfid_system.stopThread();
        break;

















###Get OAuth Details from Constants.py
# Copy your credentials from the APIs Console
# CLIENT_ID = '647866863318-s4ja5q1s5c0o7r1kes7lsgtbe30kvvkp.apps.googleusercontent.com'
# CLIENT_SECRET = '_kOgmPkPOiXLrZAnYuP913Ug'
CLIENT_ID = Constants.OAUTH_CLIENT_ID
CLIENT_SECRET = Constants.OAUTH_CLIENT_SECRET

# Check https://developers.google.com/drive/scopes for all available scopes
# OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
# OAUTH_SCOPE = 'https://spreadsheets.google.com/feeds'
OAUTH_SCOPE = Constants.OAUTH_SCOPE

# Redirect URI for installed apps
# REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# CREDENTIALS_FILE = 'credentials_file'
REDIRECT_URI = Constants.OAUTH_REDIRECT_URI
CREDENTIALS_FILE = Constants.OAUTH_CREDENTIALS_FILE

# Run through the OAuth flow and retrieve credentials
if(os.path.isfile(CREDENTIALS_FILE)): #If stored credentials is present
    #Get the stored credentials
    storage = Storage('credentials_file')
    credentials = storage.get()
    #Refresh the credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    credentials.refresh(http)
else: #If stored credentials is not present. This will occur only once.
    #Create a flow
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    #Get a url to follow for authentication
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    #Ask for the confirmation code
    code = raw_input('Enter verification code: ').strip()
    #Get the credentials
    credentials = flow.step2_exchange(code)
    #Store the credentials, so that we dont have to do oauth manually from next time.
    storage = Storage('credentials_file')
    storage.put(credentials)

#Start an app
gc = gspread.authorize(credentials)

# Open a worksheet from spreadsheet with one shot
wks = gc.open(Constants.SHEET_NAME).sheet1

wks.update_acell('B2', "it's down there somewhere, let me take another look.")

# Fetch a cell range
cell_list = wks.range('A1:B7')

print cell_list