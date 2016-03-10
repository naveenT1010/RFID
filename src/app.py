import time
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

while (True):
	# data_from_card = iq.get()
	# current_data = {"timestamp":data_from_card[0], "rfid":data_from_card[1]}
	rfas.getRowFromDB()


subprocess.Popen(["google-chrome","--kiosk","index.html"])
time.sleep(5)
subprocess.check_call(["google-chrome","--kiosk","http://google.com"])


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