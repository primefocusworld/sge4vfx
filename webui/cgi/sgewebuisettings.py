# Put your postgres DB details here
dbname="sgedb" # Put your dbname here (sgedb probably)
user="sge" # Put your dbuser here (sge probably)
host="queue1" # Put your dbhost here

# This should be an HTTP server that lets you get to where your submission
# scripts are.  For example, if you script is at /mount/blah/test.sh then
# http://<httphost>/mount/blah/test.sh should get you there
httphost = "webfiler"
