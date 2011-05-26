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
[jobNo, dummy, taskNo] = sgeid.partition(".")

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

# It's just one task, so we'll need to find out the batch starter of it
sqlQuery = "SELECT firsttask, chunk FROM jobs WHERE sgeid=" + jobNo + ";"
cur.execute(sqlQuery)
for record in cur:
	[firsttask, chunk] = record

# Tasks are only run by the first task in a batch
# The maths below works out what that batchNumber is
frameNum = int(taskNo)
fTaskNum = int(firsttask)
cNum = int(chunk)
batchNumber = frameNum - (frameNum - fTaskNum) % cNum

# Reset the tasks in that batch
sqlQuery += "UPDATE tasks SET starttime = NULL, endtime = NULL, "
sqlQuery += "returncode = NULL, attempts = attempts + 1, rhost = NULL "
sqlQuery += "WHERE sgeid=" + jobNo
sqlQuery += " AND taskno>=" + str(batchNumber) + " AND taskno<"
sqlQuery += str(batchNumber + cNum) +"; "
# Change the supplied SGE ID so that qmod restarts the batch starter task
sgeid = jobNo + "." + str(batchNumber)

cur.execute(sqlQuery)
conn.commit()
cur.close()
conn.close()

command1 = ['workers/qalter', '-ac', "rescheduled-" + str(batchNumber) +
	" " + str(jobNo)]
p1 = Popen(command1, stdout=PIPE)
theOutput = p1.communicate()[0]

# Now do the actual error clear
command2 = ['workers/qmod', '-r', sgeid]
p2 = Popen(command2, stdout=PIPE)
theOutput = p2.communicate()[0]

print json.dumps({"jobNo": jobNo, "taskNo":taskNo})
