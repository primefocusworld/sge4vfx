#!/code/tools/python-2.6.6/bin/python

import cgi

print "Content-type:text/html\r\n\r\n"

import psycopg2
import datetime

import sgewebuisettings

vals_in = cgi.FieldStorage()
sortby = vals_in.getvalue("sortby")
sortdir = vals_in.getvalue("sortdir")

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

cur.execute("SELECT * FROM jobs ORDER BY " + sortby + " " + sortdir + ";")
zebra = False
for record in cur:
	[sgeid, jobname, username, project, priority, submittime, starttime,
		endtime, firsttask, lasttask, chunk, status,
		submissionscript, donetasks] = record
	sgeid = str(sgeid)

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

	# Put in the appropriate status classes
	if status == 1:
		statusclass = "running"
	elif status == 2:
		statusclass = "error"
	elif status == 3:
		statusclass = "completed"
	else:
		statusclass = ""

	# Zebra stripe the rows
	if zebra:
		tempstring = "<tr id=\"row" + sgeid + "\" class=\"" + statusclass + " zebra\">"
	else:
		tempstring = "<tr id=\"row" + sgeid + "\" class=\"" + statusclass + "\">"
	zebra = not zebra

	tempstring += "<td><img class=\"iconbtn\" onclick=\"deleteJob("
	tempstring += sgeid + ");\" src=\"images/delete.png\" />"
	tempstring += "<a href=\"http://" + sgewebuisettings.httphost + submissionscript
	tempstring += "\"><img class=\"iconbtn\" alt=\"Submission Script\""
	tempstring += " src=\"images/script.png\" /></a>"
	tempstring += "<img class=\"iconbtn\" onclick=\"jobInfo("
	tempstring += sgeid + ");\" src=\"images/info.png\" />"
	tempstring += "</td><td>" + sgeid
	tempstring += "</td><td>" + jobname
	tempstring += "</td><td>" + username
	tempstring += "</td><td>" + str(project)
	tempstring += "</td><td>" + str(priority)
	tempstring += "</td><td>" + submittime.strftime("%d %b %H:%M:%S")
	tempstring += "</td><td alt=\"" + starttimealt + "\" class=\"starttime\">" + starttimestr
	tempstring += "</td><td>" + endtimestr
	tempstring += "</td><td" + realtimeupdate + ">" + durationstr
	tempstring += "</td><td>" + str(firsttask) + "-" + str(lasttask) + ":" + str(chunk)

	percentdone = (float(donetasks) / (float(lasttask) - float(firsttask) + 1.0)) * 100.0

	tempstring += "</td><td class=\"percentdone\">" + str(int(percentdone)) + "%"
	tempstring += "</td></tr>"
	print tempstring


cur.close()
conn.close()
