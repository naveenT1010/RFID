import subprocess
import time
try:
	# subprocess.Popen(["google-chrome","index.html"])
	# time.sleep(5)
	subprocess.Popen(["chromix-server"])
	# time.sleep(5)
	# subprocess.call(["chromix","goto","http://fb.com"])
	time.sleep(5)
	subprocess.call(["chromix","goto","http://google.com"])
	time.sleep(5)
	url = subprocess.check_output(["chromix","url"])
	print "\n\n\n"+url
except (KeyboardInterrupt):
	print "\nbye bye"