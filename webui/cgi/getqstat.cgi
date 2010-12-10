#!/usr/bin/env python

import cgi, subprocess

print "Content-type:text/xml\r\n"

command = ['workers/qstat', '-f', '-xml']

# Parse command line parameters
vals_in = cgi.FieldStorage()

# Add user
if vals_in.has_key("user"):
	user = vals_in.getvalue("user")
	command.append('-u')
	command.append(user)
# Add user
if vals_in.has_key("jobNo"):
	jobNo = vals_in.getvalue("jobNo")
	command.append('-j')
	command.append(jobNo)

p1 = subprocess.Popen(command, stdout = subprocess.PIPE)
out = p1.communicate()[0]

print out
