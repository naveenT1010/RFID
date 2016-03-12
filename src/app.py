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

#Init 
iq = multiprocessing.Queue();
oq = multiprocessing.Queue();
rfas = RfidSystem.RfidSystem(Constants.sql_db,Constants.dbTable,Constants.logTable,iq,oq);

#Run waitForCard in separate process.
if __name__ == '__main__':
	p = multiprocessing.Process(target=Reader.waitForCard,args=(iq,))
	p.start()

#for google chrome, use first command and for chromium, use the successor
subprocess.Popen(["google-chrome","--kiosk","../user_pages/index.html"])
subprocess.Popen(["chromium-browser","--kiosk","../user_pages/index.html"])
subprocess.Popen(["chromix-server"])
time.sleep(5)

db = MySQLdb.connect('localhost','pi','raspberry','rfid')
cursor = db.cursor()

meal = None

while (True):
	current_datetime = datetime.datetime.now()
	data_from_card = oq.get()
	current_data_list = {"timestamp":data_from_card[0], "rfid":data_from_card[1], "rollno":data_from_card[2], "name":data_from_card[3], "branch":data_from_card[4], "hostel":data_from_card[5]}
	#check if this is a new User
	#for new user, entries other than rfid is empty
	if rollno == None:
		#show the registration form to new user
		subprocess.call(["chromix","goto","http://google.com"])
		while not "response" in str(subprocess.check_output(["chromix","url"])):
			time.sleep(2)
		#get data from the excel and put in the logtable
	else:
		#check if the mess is currently working and review can be given now
		if 8 <= current_datetime.time().hour <= 10:
			meal = 'B'
		elif 12 <= current_datetime.time().hour <= 14:
			meal = 'L'
		elif 20 <= current_datetime.time().hour <= 22
			meal = 'D'
		else:
			print "You cant give review at this time. Go Away.."
			break

		#check for last timestamp of the same rfid
		check_query = "SELECT timestamp FROM mess WHERE rfid = " + current_data_list.rfid +" AND meal = " + meal + " ORDER BY timestamp DESC LIMIT 1"
		cursor.execute(check_query)
		previous_timestamp = cursor.fetchall()[0][0]

		#check how much time has elapsed after user reviwed this meal
		elapse_time = previous_timestamp - current_datetime

		#check if the elapsed time afer the same user has reviewed is less than 2 hours
		if divmod(elapse_time.total_seconds(),3600)[0] < 2:
			print "Sorry You have given one review for this meal. Go Away"
		
		else:
			#show the review form
			subprocess.call(["chromix","goto","PUT LOG FORM LINK"])
			while not "response" in str(subprocess.check_output(["chromix","url"])):
				time.sleep(2)





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