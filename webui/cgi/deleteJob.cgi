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

# Do the database removal
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

cur.execute("DELETE FROM jobs WHERE sgeid = " + sgeid + ";")
conn.commit()

cur.close()
conn.close()

# Now do the SGE removal
command = ['workers/qdel', sgeid]
p1 = Popen(command, stdout=PIPE)
theOutput = p1.communicate()[0]

print json.dumps({"sgeid": sgeid})
