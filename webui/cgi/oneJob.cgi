#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:text/html\r\n\r\n"

import psycopg2
import datetime
import re
import urllib

import sgewebuisettings

vals_in = cgi.FieldStorage()
sortby = vals_in.getvalue("sortby")
sortdir = vals_in.getvalue("sortdir")
jobNumber = vals_in.getvalue("jobno")
if vals_in.has_key("limit"):
	hasLimit = True
	limit = vals_in.getvalue("limit")
else:
	hasLimit = False
if vals_in.has_key("offset"):
	hasOffset = True
	offset = vals_in.getvalue("offset")
else:
	hasOffset = False

rvInstalled = True
rvString = "Opening RV.  Please wait..."

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

sqlQuery = "SELECT * FROM tasks WHERE sgeid=" + jobNumber
sqlQuery += " ORDER BY " + sortby + " " + sortdir + " "
if hasLimit:
	sqlQuery += "LIMIT " + limit + " "
	if hasOffset:
		sqlQuery += "OFFSET " + offset + " "
sqlQuery += ";"
cur.execute(sqlQuery)

zebra = False
today = datetime.date.today()
todayStr = today.strftime("%d %b")
for record in cur:
	[sgeid, taskno, starttime, endtime, attempts, returncode, rhost] = record
	sgeid = str(sgeid)
	taskno = str(taskno)
	returncode = str(returncode)
	rhost = str(rhost)

	# Format the dates into strings if not Null
	if starttime is not None:
		oldDate = ""
		newDate = ":%S"
		if todayStr != starttime.strftime("%d %b"):
			oldDate = "%d %b "
			newDate = ""
		starttimestr = starttime.strftime(oldDate + "%H:%M" + newDate)
		starttimetitle = starttime.strftime("%d %b %H:%M:%S")
		starttimealt = starttime.strftime("%m")
	else:
		starttimestr = "-"
		starttimetitle = ""
		starttimealt = ""
	if endtime is not None and starttime is not None:
		oldDate = ""
		newDate = ":%S"
		if todayStr != endtime.strftime("%d %b"):
			oldDate = "%d %b "
			newDate = ""
		endtimestr = endtime.strftime(oldDate + "%H:%M" + newDate)
		endtimetitle = endtime.strftime("%d %b %H:%M:%S")
		duration = endtime - starttime
		s = duration.seconds
		hours, remainder = divmod(s, 3600)
		minutes, seconds = divmod(remainder, 60)
		if (hours > 0):
			durationstr = '%sh %sm %ss' % (hours, minutes, seconds)
		elif (minutes > 0):
			durationstr = '%sm %ss' % (minutes, seconds)
		else:
			durationstr = '%ss' % (seconds)
		realtimeupdate = ""
	else:
		endtimestr = "-"
		durationstr = "-"
		realtimeupdate = " class=\"rtupdate\""

	# Fill in job status based on start and endtime for now
	if ((returncode != "None") and (returncode != "0")):
		statusclass="error"
	elif (returncode == "-1"):
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

	# If RV is installed, look for an output path in the job_extras table
	output_path = ""
	if rvInstalled and endtime is not None and returncode == "0":
		output_path = ""
		cur2 = conn.cursor()
		sqlQuery2 = "SELECT value FROM job_extras WHERE sgeid="
		sqlQuery2 += jobNumber + " AND key = 'output_path';"
		cur2.execute(sqlQuery2)
		for record2 in cur2:
			[output_path] = record2
			tempStr = re.sub("\.(#+)\.",
				lambda x:".%s."%str(taskno).zfill(
					len(x.groups()[0])), output_path)
                        output_path = urllib.quote(tempStr)
		cur2.close

	tempstring += "<td><img class=\"iconbtn\" onclick=\"stopTask("
	tempstring += sgeid + "," + taskno + ");\" src=\"images/delete.png\" />"
	tempstring += "<img class=\"iconbtn\" onclick=\"taskInfo("
	tempstring += sgeid + "," + taskno + ");\" src=\"images/log.png\" />"
	if output_path != "":
		tempstring += "<a onclick=\"toast('RV','" + rvString + "');\" "
		tempstring += "href=\"rvlink://" + output_path + "\">"
		tempstring += "<img class=\"iconbtn\" src=\"images/film.png\"/>"
		tempstring += "</a>"
	if returncode != "0" and returncode != "None":
		tempstring += "<img class=\"iconbtn\" onclick=\"retry(event, \'"
		tempstring += sgeid + "." + taskno + "\')\" "
		tempstring += "src=\"images/retry.png\" title=\"Retry\"/>"
	if returncode == "None" and starttime is not None:
		tempstring += "<img class=\"iconbtn\" onclick=\"reschedule(event, \'"
		tempstring += sgeid + "." + taskno + "\')\" "
		tempstring += "src=\"images/resched.png\" title=\"Kill and Retry\"/>"
	tempstring += "</td><td>" + sgeid + " - " + taskno
	tempstring += "</td><td title=\"" + starttimetitle + "\" alt=\""
	tempstring += starttimealt + "\" class=\"starttime\">" + starttimestr
	tempstring += "</td><td title=\"" + starttimetitle + "\">" + endtimestr
	# Only auto-update durations that aren't already known
	if durationstr == "-" and starttimestr != "-":
		tempstring += "</td><td" + realtimeupdate + ">" + durationstr
	else:
		tempstring += "</td><td>" + durationstr
	tempstring += "</td><td>" + returncode
	tempstring += "</td><td>" + str(attempts)
	tempstring += "</td><td>" + rhost
	tempstring += "</td></tr>"
	print tempstring

cur.close()
conn.close()
