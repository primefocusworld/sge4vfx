#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import datetime
import simplejson as json
from subprocess import Popen,PIPE

import sgewebuisettings

vals_in = cgi.FieldStorage()
sgeid = vals_in.getvalue("sgeid")

command = ['workers/qmod', '-cj', sgeid]
p1 = Popen(command, stdout=PIPE)
theOutput = p1.communicate()[0]

print json.dumps({"sgeid": sgeid})
