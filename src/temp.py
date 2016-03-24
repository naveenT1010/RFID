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
            time.sleep(5)

