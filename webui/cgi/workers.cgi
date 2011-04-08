#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi
print "Content-type:text/html\r\n\r\n"

import re
from subprocess import Popen,PIPE

vals_in = cgi.FieldStorage()
whichQueue = vals_in.getvalue("queue")

command = ['workers/qstat', "-f -q " + whichQueue]
p1 = Popen(command, stdout=PIPE)
theOutput = p1.communicate()[0]

outputList = theOutput.splitlines()
pattern = re.compile(r"" + whichQueue + "@(.*)")
zebra = False

for line in outputList:
	if whichQueue not in line:
		continue
	items = line.split()

	m = pattern.match(items[0])
	fqdn = m.group(1)
	shortName = fqdn.split(".")[0]

	[res, used, total] = items[2].split("/")
	res = int(res)
	used = int(used)
	total = int(total)
	
	loadAvg = float(items[3])
	
	status = "percent%d usageindicator" % ((float(used)/float(total))*100.0)

	# Zebra stripe the rows
	if zebra:
		tempstring = "<tr class=\"zebra\">"
	else:
		tempstring = "<tr>"
	zebra = not zebra

	tempstring += "<td>" + shortName + "</td>"
	tempstring += "<td><div class=\"slotdivcontainer\">"
	tempstring += "<div class=\"slotinfo\">" + str(used) + "/" + str(total)
	tempstring += "</div><div class=\"" + status + "\">&nbsp;</div></div></td>"
	tempstring += "<td>" + str(loadAvg) + "</td>"
	tempstring += "</tr>"
	
	print tempstring;
