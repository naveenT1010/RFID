import SimpleHTTPServer
import SocketServer
import logging
import cgi

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

import sys

iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidSystem.RfidSystem(Constants.sql_db,Constants.dbTable,Constants.logTable,iq,oq);
reader = Reader.Reader(iq)

if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8000
    I = ""
current_data = {}

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        # logging.warning("======= GET STARTED =======")
        # logging.warning(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # logging.warning("======= POST STARTED =======")
        # logging.warning(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        logging.warning("======= POST VALUES =======")
        for key in form.keys():
            queue_dict[str(key)] = form.getvalue(str(key))
        print "\n\nReached Post... printing queue: " + str(queue_dict)
        # for item in form.list:
        #     queue_dict["VM"] = 
        #     logging.warning(item)
        current_data = queue_dict
        logging.warning("\n")
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()
print "started working"
time.sleep(5)
subprocess.Popen(["chromium-browser","localhost:8000/user_pages/waiting_page.html"])
subprocess.Popen(["chromix-server"])
time.sleep(10)

db = MySQLdb.connect(Constants.sql_server,Constants.sql_user,Constants.sql_pass,Constants.sql_db)
cursor = db.cursor()

# subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/waiting_page.html"])

while (True):
    try:
        #Show the "Welcome" webpage
        print "Please use the RFID Card"

        try:
            reader.resume_read()
            data = oq.get(True, Constants.timeOut)
            reader.pause_read()
        except Queue.Empty:
            continue

        current_data_dict = {"timestamp":data[0], "rfid":data[1], "rollno":data[2], "name":data[3], "branch":data[4], "hostel":data[5]}

        #Check if this is a new user
        if current_data_dict['rollno'] == None: #If new user
            #Show the registration form to new user
            subprocess.call(["chromix","goto","localhost:8000/user_pages/user_reg.html"])
            #Waiting for user to fill the form. When filled this loop will break.
            while not "filled" in str(subprocess.check_output(["chromix","url"])):
                time.sleep(5)
            subprocess.call(["chromix","goto","localhost:8000/user_pages/processing.html"])     

            #Get credentials(using OAuth) for accessing the response sheet
            # credentials_for_access = getCredentials(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
            # Get data from the google sheet
            # sheet_record = getLatestRecord(Constants.REGISTRATION_RESPONSE_SHEET, credentials_for_access)
            
            #Put rfid data in the sheet dict and remove timestamp from sheet_record
            sheet_record['rfid'] = current_data_dict['rfid']
            sheet_record['name'] = current_data['name']
            sheet_record['rollno'] = current_data['rollno']
            sheet_record['branch'] = current_data['branch']
            sheet_record[hostel] = current_data['hostel']
            del sheet_record['timestamp']
            
            #Put this data into rfid_db in SQL
            rfas.updateDbTable(sheet_record)
            db.commit()
            #Show the "Registration Successful" webpage
            subprocess.call(["chromix","goto","localhost:8000/user_pages/reg_success.html"])        
            print "\nRegister Ho Gya... :D "
            time.sleep(5)
            subprocess.call(["chromix","goto","localhost:8000/user_pages/waiting_page.html"])

        else:
            # meal = 'B'
            # # current_datetime = datetime.datetime.now()
            # # #check if the mess is currently working and review can be given now
            # # if 8 <= current_datetime.time().hour <= 10:
            # #   meal = 'B'
            # # elif 12 <= current_datetime.time().hour <= 14:
            # #   meal = 'L'
            # # elif 20 <= current_datetime.time().hour <= 24:
            # #   meal = 'D'
            # # else:
            # #   subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/mess_closed.html"])
            # #   break

            # #Check for last timestamp of the same rfid
            # check_query = "SELECT timestamp FROM mess WHERE rfid = " + str(current_data_dict['rfid']) +' AND meal = "' +meal + '" ORDER BY timestamp DESC LIMIT 1'
            # cursor.execute(check_query)
            # previous_timestamp = cursor.fetchall()
            # print previous_timestamp

            # if not ( type(previous_timestamp) == tuple and len(previous_timestamp) == 0 ):
            #     #Show the "You have already given your review for this meal. Please come back later" webpage
            #     print "You have already done your review. Please Go Away"
            #     subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/duplicate_review.html"])   
            #     time.sleep(5)
            #     subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/index.html"])

            
            # else: #Else, if he is a existing user
            #     #Show the log form
            #     subprocess.call(["chromix","goto",Constants.LOG_FORM_URL])

            #     #Check if he filled the review form
            #     while not "Response" in str(subprocess.check_output(["chromix","url"])):
            #         time.sleep(5)
            #     subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/processing.html"]) 
                
            #     #Get credentials(using OAuth) for accessing the response sheet
            #     credentials_for_access = getCredentials(Constants.OAUTH_CLIENT_ID, Constants.OAUTH_CLIENT_SECRET, Constants.OAUTH_SCOPE, Constants.OAUTH_REDIRECT_URI)
                
            #     #Get data from the google sheet
            #     review_data = getLatestRecord(Constants.LOG_RESPONSE_SHEET,credentials_for_access)

            #     #Modify review_data according to needs before updating logtable
            #     review_data['timestamp'] = current_data_dict['timestamp']
            #     review_data['rollno'] = current_data_dict['rollno']
            #     review_data['meal'] = meal
            #     review_data['rfid'] = current_data_dict['rfid']
                
            #     #Update the log table
            #     rfas.updateLogTable(review_data)
            #     db.commit()
            #     #Show the "Your review is appreciated" webpage
            #     subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/log_success.html"])
            #     print "Your Review has been logged... Do come again.. :)"
            #     time.sleep(5)
            #     subprocess.call(["chromix","goto","file:///home/pi/Documents/RFID/user_pages/index.html"])
            pass
    except(KeyboardInterrupt, SystemExit):
        print "KeyboardInterrupt in main. Exiting"
        rfas.stopThread();
        reader.stopThread();
        break;

