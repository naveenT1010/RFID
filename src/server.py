import SimpleHTTPServer
import SocketServer
import logging
import cgi

import sys


if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8000
    I = ""


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    # def __init__(self,oq):
    #     SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self)

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
        # logging.warning("======= POST VALUES =======")
        queue_dict = {}
        for key in form.keys():
            queue_dict[str(key)] = form.getvalue(str(key))
        print queue_dict
        # for item in form.list:
        #     queue_dict["VM"] = 
        #     logging.warning(item)
        logging.warning("\n")
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

# print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()