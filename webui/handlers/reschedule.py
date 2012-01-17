from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class Reschedule(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sgeid = self.get_argument("sgeid")
        [jobNo, dummy, taskNo] = sgeid.partition(".")
        
        # Since it's just one task, we have to find out which batch task it
        # belongs to.  e.g. 1-10:5 would have a result of 1 or 6 no matter
        # which task needed rescheduling
        sqlQuery = "SELECT firsttask,chunk FROM jobs WHERE sgeid=" + jobNo + ";"
        firstCursor = yield gen.Task(self.db.execute, sqlQuery)
        
        # Get the firsttask number and the batch size
        for record in firstCursor:
            [firsttask, chunk] = record
        
        # Now work out what that appropriate batch number task is
        frameNum = int(taskNo)
        fTaskNum = int(firsttask)
        cNum = int(chunk)
        batchNumber = frameNum - (frameNum - fTaskNum) % cNum
        
        # Build the query to reset the tasks in that batch
        sqlQuery = "UPDATE tasks SET starttime = NULL, endtime = NULL, "
        sqlQuery += "returncode = NULL, attempts = attempts + 1, rhost = NULL "
        sqlQuery += "WHERE sgeid=" + jobNo
        sqlQuery += " AND taskno>=" + str(batchNumber) + " AND taskno<"
        sqlQuery += str(batchNumber + cNum) +";"
        
        # Now change sgeid so it points to the batch task which may not be the
        # original task number
        sgeid = jobNo + "." + str(batchNumber)
        # and the command to actually reschedule the task in SGE
        command = str(self.shellCmdsLocation + "qmod -r " + sgeid)
        
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