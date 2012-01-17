from handlers.base import BaseHandler

import tornado.web
from tornado import gen
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class DeleteComplete(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params 
        deleteOnlyOld = self.get_argument("old", False)
        user = self.get_argument("user")
        
        # Set up SQL to change it in the DB
        sqlQuery = "DELETE FROM jobs WHERE "
        sqlQuery += "username='" + user + "' AND status=3 "
        if deleteOnlyOld:
            sqlQuery += "AND endtime < 'yesterday'"
        sqlQuery += ";"
        
        # ASync run the delete
        dbResult = yield gen.Task(self.db.execute, sqlQuery)
        
        # Return some JSON saying done.
        # TODO: Check the return value for errors
        output = json.dumps({"done": True})
        self.write(output)
        self.finish() 