#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import datetime
import simplejson as json

import sgewebuisettings

vals_in = cgi.FieldStorage()
sgeid = vals_in.getvalue("sgeid")
frame = vals_in.getvalue("frame")

# Do the database update (set return code to -1)
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

sqlQuery = "SELECT stdout,stderr FROM jobs WHERE sgeid = " + sgeid + ";"
cur.execute(sqlQuery)
conn.commit()

cur.execute(sqlQuery)
for record in cur:
	[stdout, stderr] = record
	soFilename = stdout + "." + frame
	seFilename = stderr + "." + frame

	# Stdout
	try:
		f = open(soFilename, 'r')
		stdoutReturn = f.read()
		stdoutReturn = stdoutReturn.replace("\n","<br />\n")
	except IOError as e:
		stdoutReturn = "No stdout"

	# Stderr
	try:
                f = open(seFilename, 'r')
                stderrReturn = f.read()
        except IOError as e:
                stderrReturn = "No stderr"

cur.close()
conn.close()

print json.dumps({"stdout":stdoutReturn, "stderr":stderrReturn})
