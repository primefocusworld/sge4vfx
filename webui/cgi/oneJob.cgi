#!/code/tools/python-2.6.6/bin/python

import cgi

print "Content-type:text/html\r\n\r\n"

import psycopg2
import datetime

import sgewebuisettings

vals_in = cgi.FieldStorage()
sortby = vals_in.getvalue("sortby")
sortdir = vals_in.getvalue("sortdir")
jobNumber = vals_in.getvalue("jobno")

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

sqlQuery = "SELECT * FROM tasks WHERE sgeid=" + jobNumber
sqlQuery += " ORDER BY " + sortby + " " + sortdir + ";"
cur.execute(sqlQuery)

zebra = False
for record in cur:
	[sgeid, taskno, starttime, endtime, retries, returncode] = record
	sgeid = str(sgeid)
	taskno = str(taskno)
	returncode = str(returncode)

	# Format the dates into strings if not Null
	if starttime is not None:
		starttimestr = starttime.strftime("%d %b %H:%M:%S")
		starttimealt = starttime.strftime("%m")
	else:
		starttimestr = "-"
		starttimealt = ""
	if endtime is not None:
		endtimestr = endtime.strftime("%d %b %H:%M:%S")
		duration = endtime - starttime
		s = duration.seconds
		hours, remainder = divmod(s, 3600)
		minutes, seconds = divmod(remainder, 60)
		durationstr = '%sh %sm %ss' % (hours, minutes, seconds)
		realtimeupdate = ""
	else:
		endtimestr = "-"
		durationstr = "-"
		realtimeupdate = " class=\"rtupdate\""

	# Fill in job status based on start and endtime for now
	if (returncode == "-1"):
		statusclass="other"
	elif ((starttime is not None) and (endtime is None)):
		statusclass="running"
	elif ((starttime is not None) and (endtime is not None)):
		statusclass="completed"
	else:
		statusclass=""

	# Zebra stripe the rows
	if zebra:
		tempstring = "<tr id=\"row" + sgeid + "-" + taskno
		tempstring += "\" class=\"" + statusclass+ " zebra\">"
	else:
		tempstring = "<tr id=\"row" + sgeid + "-" + taskno
		tempstring += "\" class=\"" + statusclass+ "\">"
	zebra = not zebra

	tempstring += "<td><img class=\"iconbtn\" onclick=\"stopTask("
	tempstring += sgeid + "," + taskno + ");\" src=\"images/delete.png\" />"
	tempstring += "<img class=\"iconbtn\" onclick=\"taskInfo("
	tempstring += sgeid + "," + taskno + ");\" src=\"images/info.png\" />"
	tempstring += "</td><td>" + sgeid + " - " + taskno
	tempstring += "</td><td alt=\"" + starttimealt + "\" class=\"starttime\">" + starttimestr
	tempstring += "</td><td>" + endtimestr
	tempstring += "</td><td" + realtimeupdate + ">" + durationstr
	tempstring += "</td><td>" + returncode
	tempstring += "</td></tr>"
	print tempstring

cur.close()
conn.close()
