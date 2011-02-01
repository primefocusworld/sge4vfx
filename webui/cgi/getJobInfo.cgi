#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi
import xml.dom.minidom

print "Content-type:application/json\r\n\r\n"

import simplejson as json
from subprocess import Popen,PIPE

vals_in = cgi.FieldStorage()
sgeid = vals_in.getvalue("sgeid")

# Run qstat
command = ['workers/qstat', '-j', sgeid, '-xml']
p1 = Popen(command, stdout=PIPE)
theXML = p1.communicate()[0]

# Parse the XML from qstat
dom = xml.dom.minidom.parseString(theXML)

# Submission Script (don't need to get this but an easy example)
scriptFileArray = dom.getElementsByTagName("JB_script_file")
if scriptFileArray.length != 0:
	scriptFile = scriptFileArray[0].firstChild.nodeValue

# Get the stdout path if set
stdoutArray = dom.getElementsByTagName("JB_stdout_path_list")
if stdoutArray.length != 0:
	PN_path = stdoutArray[0].getElementsByTagName("PN_path")
	stdoutPath = PN_path[0].firstChild.nodeValue
else:
	stdoutPath = "Unknown"

# Get the stderr path if set
stderrArray = dom.getElementsByTagName("JB_stderr_path_list")
if stderrArray.length != 0:
	PN_path = stderrArray[0].getElementsByTagName("PN_path")
	stderrPath = PN_path[0].firstChild.nodeValue
else:
	stderrPath = "Unknown"

print json.dumps({"scriptFile": scriptFile, "stdout": stdoutPath, "stderr": stderrPath})
