#Simple array task web interface

##License

As this (the contents of the webui folder) uses GPL components, the license remains and is included in the LICENSE file

##Install

###SGE bits

apache (or whatever user it's running as, must be a manager in SGE so it can delete jobs.  The machine the webserver's running on must be a submit host for the same reason.

###Postgres

You'll need to setup the database first.  Have a look at the README.md in the db directory if you haven't already.

###Memcached

Make sure memcache is installed and running on port 11211

###Apache

1. Set up an apache install somewhere and put these files either in the root or a subdirectory
2. Make the cgi directory a ScriptAlias so the CGI stuff can be executed.
Here's an example httpd/conf.d/theq.conf

    ScriptAlias /theq/cgi/ /wherever_it_is/cgi/
    Alias /theq/ /wherever_it_is/

3. Reload/restart httpd/apache
4. In all the CGI worker scripts, put the path of your SGE settings.sh so that the environment can be sourced (I'm sure there's a way to do this once in a file elsewhere - anyone??)
5. In cgi/sgewebuisettings.py put your database settings

It should be working now if you point your browser at <webserver>/theq/ (assuming you used the example conf above).  It'll probably show nothing though because there's nothing in the DB.  Have a look in the scripts directory for how to submit.

##ToDo

* Multi-user support with a simple text input at the top for username
* Caching qstat output
* Task details
* Dependency graphs

##Notes

* It's worth noting that I've been developing almost entirely in Google Chrome.  I've checked every now and then that it looks ok in Firefox, but it's certainly not as pretty as in Chrome.  Just use Chrome :-)
* It assumes everything is an array task