#!/code/tools/python-2.6.6/bin/python

import cgi

print "Content-type:application/json\r\n\r\n"

import psycopg2
import datetime
import simplejson as json
from subprocess import Popen,PIPE

import sgewebuisettings

vals_in = cgi.FieldStorage()
sgeid = vals_in.getvalue("sgeid")
taskno = vals_in.getvalue("taskno")

# Do the database update (set return code to -1)
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

sqlQuery = "UPDATE tasks SET returncode = -1 WHERE sgeid = " + sgeid
sqlQuery += " AND taskno = " + taskno + ";"
cur.execute(sqlQuery)
conn.commit()

# For the time being, we'll set cancelled tasks as done.  I know it's counter-
# intuitive, but otherwise the job will show as running forever.  This can
# probably be fixed with a cron that changes the status of jobs based on qstat
# output or something...
# This tests if the tasks have a starttime because if they do, they're running
# (or have been run) and therefore the epilog script will (or will have) run
sqlQuery = "UPDATE jobs SET donetasks = donetasks + 1 FROM tasks"
sqlQuery += " WHERE jobs.sgeid = " + sgeid + " AND jobs.sgeid = tasks.sgeid"
sqlQuery += " AND tasks.taskno = " + taskno + " AND tasks.starttime IS NULL;"
cur.execute(sqlQuery)
conn.commit()

cur.close()
conn.close()

# Now do the SGE removal
command = ['workers/qdel', sgeid + "." + taskno]
p1 = Popen(command, stdout=PIPE)
theOutput = p1.communicate()[0]

print json.dumps({"sgeid": sgeid, "taskno": taskno})
