#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import datetime
import simplejson as json
from subprocess import Popen,PIPE

import sgewebuisettings

dbname="sgedb"
user="sge"
removeToday=True
already_got_criteria=False
host="queue1"

# Get the CGI values from the form submission
vals_in = cgi.FieldStorage()
if vals_in.has_key("user"):
	user = vals_in.getvalue("user")
else:
	user = ""
if vals_in.has_key("old"):
	removeToday = False

# Do the database removal
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
deleteCur = conn.cursor()

psqlcommand = "SELECT sgeid FROM jobs WHERE"
if removeToday:
        psqlcommand += " status=" + str(2)
        already_got_criteria = True
if already_got_criteria:
        psqlcommand += " AND"
psqlcommand += " username='" + user + "'"
if not removeToday:
        psqlcommand += " AND endtime < 'yesterday'"
psqlcommand += ";"

deleteCur.execute(psqlcommand)
for record in deleteCur:
	[sgeid] = record

	command = ['workers/qdel', str(sgeid)]
	p1 = Popen(command, stdout=PIPE)
	theOutput = p1.communicate()[0]

deleteCur.close()

cur = conn.cursor()

psqlcommand = "DELETE FROM jobs WHERE"
if removeToday:
	psqlcommand += " status=" + str(2)
	already_got_criteria = True
if already_got_criteria:
	psqlcommand += " AND"
psqlcommand += " username='" + user + "'"
if not removeToday:
	psqlcommand += " AND endtime < 'yesterday'"
psqlcommand += ";"

cur.execute(psqlcommand)
conn.commit()

cur.close()
conn.close()

print json.dumps({"result":"success"})
