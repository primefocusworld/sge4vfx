#Web UI
The Web UI is now based on Tornado.  I recommend using supervisord to run it backed onto nginx.
If you look in the 'setup' subdirectory you'll find some example configs.

Uses the following:

* http://www.tornadoweb.org/
* https://github.com/bueda/tornado-boilerplate
* https://github.com/FSX/momoko
* http://initd.org/psycopg/
* http://pypi.python.org/pypi/simplejson/
* https://github.com/janl/mustache.js/
* http://jquery.com/
* http://jqueryui.com/

The JS is still pretty ugly and needs a rewrite with a decent MVC framework.  It works though...
