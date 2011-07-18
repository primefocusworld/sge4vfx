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
newPriority = vals_in.getvalue("priority")

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

# Reset the tasks in that batch
sqlQuery = "UPDATE jobs SET priority = " + newPriority
sqlQuery += "WHERE sgeid=" + sgeid +"; "

cur.execute(sqlQuery)
conn.commit()
cur.close()
conn.close()

command1 = ['workers/qalter', '-p', newPriority + " " + sgeid]
p1 = Popen(command1, stdout=PIPE)
theOutput = p1.communicate()[0]

print json.dumps({"jobNo": sgeid})
