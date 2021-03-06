import json
import tornado.web

import momoko
import memcache

import logging
import os
from settings import ROOT
logger = logging.getLogger('theq2.' + __name__)


class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    
    def initialize(self):
        self._shellCmdsLocation = os.path.join(ROOT, "shell_cmds/")
        self._cacheDuration = 5
    
    @property
    def shellCmdsLocation(self):
        return self._shellCmdsLocation
    
    @property
    def cacheDuration(self):
        return self._cacheDuration
    
    @property
    def mc(self):
        # Create a memcache client and attach it to the application object
        if not hasattr(self.application, 'mc'):
            self.application.mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        return self.application.mc

    @property
    def db(self):
        # Create a database connection when a request handler is called
        # and store the connection in the application object.
        if not hasattr(self.application, 'db'):
            self.application.db = momoko.AsyncClient({
                'host': 'queue1',
                'database': 'sgedb',
                'user': 'sge',
                'password': '',
                'min_conn': 1,
                'max_conn': 20,
                'cleanup_timeout': 10
            })
        return self.application.db

    def load_json(self):
        """Load JSON from the request body and store them in
        self.request.arguments, like Tornado does by default for POSTed form
        parameters.

        If JSON cannot be decoded, raises an HTTPError with status 400.
        """
        try:
            self.request.arguments = json.loads(self.request.body)
        except ValueError:
            msg = "Could not decode JSON: %s" % self.request.body
            logger.debug(msg)
            raise tornado.web.HTTPError(400, msg)

    def get_json_argument(self, name, default=None):
        """Find and return the argument with key 'name' from JSON request data.
        Similar to Tornado's get_argument() method.
        """
        if default is None:
            default = self._ARG_DEFAULT
        if not self.request.arguments:
            self.load_json()
        if name not in self.request.arguments:
            if default is self._ARG_DEFAULT:
                msg = "Missing argument '%s'" % name
                logger.debug(msg)
                raise tornado.web.HTTPError(400, msg)
            logger.debug("Returning default argument %s, as we couldn't find "
                    "'%s' in %s" % (default, name, self.request.arguments))
            return default
        arg = self.request.arguments[name]
        logger.debug("Found '%s': %s in JSON arguments" % (name, arg))
        return arg
