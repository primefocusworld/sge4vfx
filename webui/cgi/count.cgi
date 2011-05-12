#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import simplejson as json

import sgewebuisettings

# Get the CGI values from the form submission
vals_in = cgi.FieldStorage()
sortby = vals_in.getvalue("sortby")
sortdir = vals_in.getvalue("sortdir")
if vals_in.has_key("username"):
	user = vals_in.getvalue("username")
else:
	user = ""
if vals_in.has_key("projname"):
	project = vals_in.getvalue("projname")
else:
	project = ""
if vals_in.has_key("done"):
	done = True
else:
	done = False
if vals_in.has_key("running"):
	running = True
else:
	running = False
if vals_in.has_key("error"):
	error = True
else:
	error = False
if vals_in.has_key("wait"):
	wait = True
else:
	wait = False

# Connect to the Postgres DB
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

# Compose the query using all the submitted filters
gotawherealready=False
gotastatusalready=False
psqlcommand = "SELECT count(*) FROM jobs "
if user != "":
	psqlcommand += "WHERE username='" + user + "' "
	gotawherealready = True
if project != "":
	if gotawherealready:
		psqlcommand += "AND project='" + project + "' "
	else:
		psqlcommand += "WHERE project='" + project + "' "
	gotawherealready = True
if done:
	if gotawherealready:
		psqlcommand += "AND (status=3 "
	else:
		psqlcommand += "WHERE (status=3"
	gotawherealready = True
	gotastatusalready = True
if running:
	if gotastatusalready:
		psqlcommand += "OR status=1 "
	else:
		if gotawherealready:
			psqlcommand += "AND (status=1 "
		else:
			psqlcommand += "WHERE (status=1"
	gotawherealready = True
	gotastatusalready = True
if wait:
	if gotastatusalready:
		psqlcommand += "OR status=0 "
	else:
		if gotawherealready:
			psqlcommand += "AND (status=0 "
		else:
			psqlcommand += "WHERE (status=0"
	gotawherealready = True
	gotastatusalready = True
if error:
	if gotastatusalready:
		psqlcommand += "OR status=2 "
	else:
		if gotawherealready:
			psqlcommand += "AND (status=2 "
		else:
			psqlcommand += "WHERE (status=2 "
	gotawherealready = True
	gotastatusalready = True
if gotastatusalready:
	psqlcommand += ") "
psqlcommand += ";"

count = 0

# Execute the SQL query
cur.execute(psqlcommand)
for record in cur:
	[count] = record

cur.close()
conn.close()

print json.dumps({"count":count})
