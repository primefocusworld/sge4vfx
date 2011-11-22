from handlers.base import BaseHandler

import tornado.web
from tornado import gen
import simplejson as json
from async_process import call_subprocess

import logging
logger = logging.getLogger('theq2.' + __name__)

class DeleteErrors(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        user = self.get_argument("user")
        
        # Set up SQL to find the jobs to be deleted from SGE
        sqlQuery = "SELECT sgeid FROM jobs WHERE "
        sqlQuery += "username='" + user + "' AND status=2;"
        logger.info(sqlQuery)
        
        # ASync run the delete
        jobCursor = yield gen.Task(self.db.execute, sqlQuery)
        # Now for every row in the returned jobTable cursor
        for record in jobCursor:
            [sgeid] = record
            command = str(self.shellCmdsLocation + "qdel " + str(sgeid))
            # qdel it
            output = yield gen.Task(call_subprocess, self, command)
        
        # Set up SQL to do the DB side of the delete
        sqlQuery = "DELETE FROM jobs WHERE "
        sqlQuery += "username='" + user + "' AND status=2;"
        
        # ASync run the delete
        dbOut = yield gen.Task(self.db.execute, sqlQuery)
        
        # Return some JSON saying done.
        # TODO: Check the return value for errors
        output = json.dumps({"done": True})
        self.write(output)
        self.finish() 