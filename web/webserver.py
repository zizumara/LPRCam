#!/usr/bin/python3
# webserver.py

"""
A basic web page server.
"""

import os, sys
from http.server import HTTPServer, CGIHTTPRequestHandler

webdir = '/home/pizzle/web'
port = 2223
# NOTE: Any non-standard port above 1024 can be used here.  The purpose
# of avoiding the default port 80 is to hide the site from web crawlers
# for security purposes.

os.chdir(webdir)
serverAddr = ('', port)
serverObj = HTTPServer(serverAddr, CGIHTTPRequestHandler)
serverObj.serve_forever()
