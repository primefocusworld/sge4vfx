#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import simplejson as json

import sgewebuisettings

# Get the CGI values from the form submission
vals_in = cgi.FieldStorage()
if vals_in.has_key("jobno"):
	jobno = vals_in.getvalue("jobno")
else:
	jobno = "0"

# Connect to the Postgres DB
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

# Compose the query using all the submitted filters
psqlcommand = "SELECT count(*) FROM tasks "
if jobno != "0":
	psqlcommand += "WHERE sgeid='" + jobno + "';"

count = 0

# Execute the SQL query
cur.execute(psqlcommand)
for record in cur:
	[count] = record

cur.close()
conn.close()

print json.dumps({"count":count})
