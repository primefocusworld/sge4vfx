#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:text/html\r\n\r\n"

import psycopg2
import datetime

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
psqlcommand = "SELECT * FROM jobs "
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
psqlcommand += "ORDER BY " + sortby + " " + sortdir + ";"

# Execute the SQL query
cur.execute(psqlcommand)
zebra = False
today = datetime.date.today()
todayStr = today.strftime("%d %b")
for record in cur:
	[sgeid, jobname, username, project, priority, submittime, starttime,
		endtime, firsttask, lasttask, chunk, status,
		submissionscript, donetasks] = record
	sgeid = str(sgeid)

	# Format the dates into strings if not Null
	oldDate = ""
	newDate = ":%S"
	if todayStr != submittime.strftime("%d %b"):
		oldDate = "%d %b "
		newDate = ""
	submittimestr = submittime.strftime(oldDate + "%H:%M" + newDate)
	submittimetitle = submittime.strftime("%d %b %H:%M:%S")

	if starttime is not None:
		oldDate = ""
		newDate = ":%S"
		if todayStr != starttime.strftime("%d %b"):
			oldDate = "%d/%m "
			newDate = ""
		starttimestr = starttime.strftime(oldDate + "%H:%M" + newDate)
		starttimetitle = starttime.strftime("%d %b %H:%M:%S")
		starttimealt = starttime.strftime("%m")
	else:
		starttimestr = "-"
		starttimetitle = ""
		starttimealt = ""
	if endtime is not None:
		oldDate = ""
		newDate = ":%S"
		if todayStr != endtime.strftime("%d %b"):
			oldDate = "%d/%m "
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
		tempstring = "<tr onclick=\"addJobTab(" + sgeid + ");\""
		tempstring += "id=\"row" + sgeid + "\" class=\"" + statusclass
		tempstring += " zebra\">"
	else:
		tempstring = "<tr onclick=\"addJobTab(" + sgeid + ");\""
		tempstring += "id=\"row" + sgeid + "\" class=\"" + statusclass
		tempstring += "\">"
	zebra = not zebra

	tempstring += "<td><img class=\"iconbtn\" onclick=\"deleteJob(event, "
	tempstring += sgeid + ");\" src=\"images/delete.png\" />"
	tempstring += "<a onclick=\"event.stopPropagation();\" "
	tempstring += "href=\"http://" + sgewebuisettings.httphost + submissionscript
	tempstring += "\"><img class=\"iconbtn\" alt=\"Submission Script\""
	tempstring += " src=\"images/script.png\" /></a>"
	tempstring += "<img class=\"iconbtn\" onclick=\"jobInfo(event, "
	tempstring += sgeid + ");\" src=\"images/info.png\" />"
	tempstring += "</td><td>" + sgeid
	tempstring += "</td><td>" + jobname
	tempstring += "</td><td>" + username
	tempstring += "</td><td>" + str(project)
	tempstring += "</td><td>" + str(priority)
	tempstring += "</td><td title=\"" + submittimetitle + "\">" + submittimestr
	tempstring += "</td><td title=\"" + starttimetitle + "\" alt=\""
	tempstring += starttimealt + "\" class=\"starttime\">" + starttimestr
	tempstring += "</td><td title=\"" + starttimetitle + "\">" + endtimestr
	tempstring += "</td><td" + realtimeupdate + ">" + durationstr
	tempstring += "</td><td>" + str(firsttask) + "-" + str(lasttask) + ":" + str(chunk)

	percentdone = (float(donetasks) / (float(lasttask) - float(firsttask) + 1.0)) * 100.0

	tempstring += "</td><td class=\"percentdone\">" + str(int(percentdone)) + "% (" + str(donetasks) + ")"
	tempstring += "</td></tr>"
	print tempstring


cur.close()
conn.close()
