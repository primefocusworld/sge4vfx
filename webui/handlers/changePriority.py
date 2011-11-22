from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class ChangePriority(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sgeid = self.get_argument("sgeid")
        priority = self.get_argument("priority", "0")
        
        # Set up SQL to change it in the DB
        sqlQuery = "UPDATE jobs SET priority = " + priority
        sqlQuery += "WHERE sgeid=" + sgeid +"; "
        
        # and the command to actually mod SGE
        command = str(self.shellCmdsLocation + "qalter -p "
                      + priority + " " + sgeid)
        
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