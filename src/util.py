

#Function to convert uid into rfid
def uid_to_rfid(uid):
    rfid = uid[0]*(16**6) + uid[1]*(16**4) + uid[2]*(16**2) + uid[3];
    return rfid;