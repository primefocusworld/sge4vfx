from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class DeleteJob(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sgeid = self.get_argument("sgeid")
        
        # Set up SQL to delete it from the DB
        sqlQuery = "DELETE FROM jobs WHERE sgeid=" + str(sgeid) + ";"
        
        # and the command to actually mod SGE
        command = str(self.shellCmdsLocation + "qdel " + str(sgeid))
        
        # ASync run the two tasks
        dbResult, shellOut = yield [
            gen.Task(self.db.execute, sqlQuery),
            gen.Task(call_subprocess, self, command)
        ]
        
        # Return some JSON saying done.
        # TODO: Check the return values for errors
        output = json.dumps({"done": True})
        self.write(output)
        self.finish() 