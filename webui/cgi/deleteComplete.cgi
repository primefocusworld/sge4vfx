#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import datetime
import simplejson as json

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
cur = conn.cursor()

psqlcommand = "DELETE FROM jobs WHERE"
if removeToday:
	psqlcommand += " status=" + str(3)
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
