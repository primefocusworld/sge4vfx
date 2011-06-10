#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi
print "Content-type:application/json\r\n\r\n"

import re
import simplejson as json
from subprocess import Popen,PIPE

vals_in = cgi.FieldStorage()
whichQueue = vals_in.getvalue("queue")

command = ['workers/qstat', "-g c -q " + whichQueue]
p1 = Popen(command, stdout=PIPE)
theOutput = p1.communicate()[0]

outputList = theOutput.splitlines()

used = 0
avail = 0
total = ""
usedpc = 0
availpc = 0
broken = 0
brokenpc = 0
suspended = 0

for line in outputList:
	if whichQueue not in line:
		continue
	items = line.split()

	used = int(items[2])
	suspended = int(items[6])
	avail = int(items[4])
	total = int(items[5])
	broken = int(items[7])

good = total - broken - suspended
goodpc = (float(good) / float(total)) * 100.0

if used != 0:
	usedpc = (float(used) / float(good)) * 100.0
else:
	usedpc = 0.0
if broken != 0:
	brokenpc = (float(broken) / float(total)) * 100.0
else:
	brokenpc = 0.0
if suspended != 0:
	suspendedpc = (float(suspended) / float(total)) * 100.0
else:
	suspendedpc = 0.0

availpc = 100.0 - usedpc

usedpc = "%.1f" % usedpc
availpc = "%.1f" % availpc
brokenpc = "%.1f" % brokenpc
suspendedpc = "%.1f" % suspendedpc
goodpc = "%.1f" % goodpc

print json.dumps({"total":total, "used":used,
	"avail":avail, "usedpc":usedpc,
	"availpc": availpc, "broken":broken,
	"brokenpc":brokenpc, "good":good,
	"goodpc":goodpc, "suspended":suspended,
	"suspendedpc":suspendedpc})
