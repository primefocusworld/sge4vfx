#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi
print "Content-type:text/html\r\n\r\n"

import re
from subprocess import Popen,PIPE
import memcache

cache_expiry = 5

vals_in = cgi.FieldStorage()
whichQueue = vals_in.getvalue("queue")

# Connect to memcache server
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
# Try and get the value from memcache
output = mc.get("theQ-workers-" + whichQueue);
# If it's not there
if not output:
	# Run qstat to get the info and format the table
	command = ['workers/qstat', "-f -q " + whichQueue]
	p1 = Popen(command, stdout=PIPE)
	theOutput = p1.communicate()[0]

	outputList = theOutput.splitlines()
	pattern = re.compile(r"" + whichQueue + "@(.*)")
	zebra = False

	output = ""

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
	
		if items[3] != "-NA-":
			loadAvg = float(items[3])
		else:
			loadAvg = "NA"

		status = "percent%d usageindicator" % ((float(used)/float(total))*100.0)
		if len(items) > 5:
			machineStates = items[5]
			if machineStates.find("u") != -1:
				trclass = "error"
			else:
				trclass = "warning"
			status = ""
		else:
			trclass = ""
			machineStates = ""

		# Zebra stripe the rows
		if zebra:
			tempstring = "<tr class=\"" + trclass + " zebra\">"
		else:
			tempstring = "<tr class=\"" + trclass + "\">"
		zebra = not zebra

		tempstring += "<td>" + shortName + "</td>"
		tempstring += "<td><div class=\"slotdivcontainer\">"
		tempstring += "<div class=\"slotinfo\">" + str(used) + "/" + str(total)
		tempstring += "</div><div class=\"" + status + "\">&nbsp;</div></div></td>"
		tempstring += "<td>" + str(loadAvg) + "</td>"
		tempstring += "<td>" + machineStates + "</td>"
		tempstring += "</tr>"
		
		output += tempstring
	
	# Set it in memcache
	mc.set("theQ-workers-" + whichQueue, output, cache_expiry)

# Finally print it
print output
