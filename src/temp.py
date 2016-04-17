import cgitb; cgitb.enable()
import cgi
import sys

form = cgi.FieldStorage()
name = form['name'].value
print 'Hello ' + name