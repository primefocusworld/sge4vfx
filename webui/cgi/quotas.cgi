#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi
print "Content-type:text/html\r\n\r\n"

import memcache

cache_expiry = 5

vals_in = cgi.FieldStorage()
whichQueue = vals_in.getvalue("queue")

# Connect to memcache server
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
# Try and get the value from memcache
#output = mc.get("theQ-quotas-" + whichQueue);
output=""
# If it's not there
if not output:
	import re
	from subprocess import Popen,PIPE

	# Run qstat to get the info and format the table
	command = ['workers/qquota-all', "-q " + whichQueue]
	p1 = Popen(command, stdout=PIPE)
	theOutput = p1.communicate()[0]

	outputList = theOutput.splitlines()

	output = ""
	zebra = False

	for line in outputList:
		if "slots" not in line:
			continue
		items = line.split()

		slot_use = items[1]
		slot_use_right = slot_use.split("=")[1]
		slots_used = slot_use_right.split("/")[0]
		username = items[3]

		if zebra:
			tempstring = "<tr class=\"zebra\">"
		else:
			tempstring = "<tr>"
		zebra = not zebra

		tempstring += ("<td>" + username + 
			"</td><td>" + slots_used + "</td></tr>")
		output += tempstring
	
	# Set it in memcache
	mc.set("theQ-quotas-" + whichQueue, output, cache_expiry)

# Finally print it
print output
