#SQL CONSTANTS
sql_server = "localhost"
sql_user = "pi"#"pi"
sql_pass = "raspberry"#""
sql_db = "rfid"#"IITG"
dbTable = "rfid_db"#"students"
logTable = "mess"

#RFID System Constants
timeOut = 5 #Time to wait for data from iq in RfidSystem.
timeSleep = 5 #Time that the system sleeps after reading a card, to avoid multiple reads.

#OAUTH Constants
#raghu
# OAUTH_CLIENT_ID ='647866863318-8gdadgl7js9d5o0bbrkcds7as6s420p5.apps.googleusercontent.com'
#naveen
OAUTH_CLIENT_ID ='943930483169-j9bnqkvhq385c7ph7i82sjh6a4c8l2q1.apps.googleusercontent.com'
#raghu
# OAUTH_CLIENT_SECRET = 'KFKZBajk5KA7pUQ_cTduz6z6' #'t-tn-1L1waC8bamHCyRa0kQq'
#naveen
OAUTH_CLIENT_SECRET = 't-tn-1L1waC8bamHCyRa0kQq'

OAUTH_SCOPE = 'https://spreadsheets.google.com/feeds'
OAUTH_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
OAUTH_CREDENTIALS_FILE = 'credentials_file'

#FORM AND RESPONSES
REGISTRATION_FORM_URL = 'http://goo.gl/forms/rrLQGy3rze'
REGISTRATION_RESPONSE_SHEET = 'RFID Responses'
LOG_FORM_URL = 'http://goo.gl/forms/Vt4ehx26zv'
LOG_RESPONSE_SHEET = 'MESS Responses'