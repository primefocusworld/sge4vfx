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

wholeJob = True
if taskNo:
	wholeJob = False

conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

# Get a count of how many tasks where successfully completed
sqlQuery = "SELECT COUNT(*) FROM TASKS WHERE returncode=0 AND sgeid="
sqlQuery += jobNo + ";"
cur.execute(sqlQuery)
for record in cur:
	[goodCount] = record

# If it's the whole job
if wholeJob:
	# If donetasks was 100%, then set it to pending, otherwise running
	sqlQuery = "UPDATE jobs SET status = 0 WHERE sgeid=" + jobNo + " AND "
	sqlQuery += "donetasks = (lasttask - firsttask + 1); "
	sqlQuery += "UPDATE jobs SET status = 1 WHERE sgeid=" + jobNo + " AND "
	sqlQuery += "donetasks != (lasttask - firsttask + 1); "
	# Now decrease donetasks by that number and set endtime NULL
	sqlQuery += "UPDATE jobs SET endtime = NULL, donetasks=(" + str(goodCount)
	sqlQuery += ") WHERE sgeid=" + jobNo + "; "
	# Also, reset any tasks that don't have returncode 0
	sqlQuery += "UPDATE tasks SET starttime = NULL, endtime = NULL, "
	sqlQuery += "returncode = NULL, rhost = NULL WHERE sgeid=" + jobNo
	sqlQuery += " AND returncode != 0;"
else:
	# If it's just one task, we'll need to find out the batch starter of it
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
	
	# Now decrease donetasks by the size of a batch
	sqlQuery = "UPDATE jobs SET endtime = NULL, donetasks=(donetasks-chunk) "
	sqlQuery += "WHERE sgeid=" + jobNo + "; "
	sqlQuery += "UPDATE jobs SET status = 0 WHERE donetasks="
	sqlQuery += str(goodCount) + " AND sgeid=" + jobNo + "; "
	# and reset the tasks in that batch
	sqlQuery += "UPDATE tasks SET starttime = NULL, endtime = NULL, "
	sqlQuery += "returncode = NULL, rhost = NULL WHERE sgeid=" + jobNo
	sqlQuery += " AND taskno>=" + str(batchNumber) + " AND taskno<"
	sqlQuery += str(batchNumber + cNum) +"; "
	# Change the supplied SGE ID so that qmod restarts the batch starter task
	sgeid = jobNo + "." + str(batchNumber)

cur.execute(sqlQuery)
conn.commit()
cur.close()
conn.close()

# Now do the actual error clear
command = ['workers/qmod', '-cj', sgeid]
p1 = Popen(command, stdout=PIPE)
theOutput = p1.communicate()[0]

print json.dumps({"jobNo": jobNo, "taskNo":taskNo})
