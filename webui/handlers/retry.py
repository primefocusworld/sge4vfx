from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class Retry(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sgeid = self.get_argument("sgeid")
        [jobNo, dummy, taskNo] = sgeid.partition(".")
        
        wholeJob = True
        if taskNo:
            wholeJob = False
        
        # Find out how many tasks have been successfully completed
        sqlQuery = "SELECT COUNT(*) FROM TASKS WHERE returncode=0 AND sgeid="
        sqlQuery += jobNo + ";"
        
        cur = yield gen.Task(self.db.execute, sqlQuery)
        
        for record in cur:
            [goodCount] = record
        
        if wholeJob:
            sqlQuery = self.buildQueryWholeJob(jobNo, goodCount)
        else:
            # Since it's just one task, we'll need to find out
            # the batch starter of it (task 2 in 1-5:1 would be 1 for example)
            sqlQuery = "SELECT firsttask,chunk FROM jobs WHERE sgeid="
            sqlQuery += jobNo + ";"
            
            cur = yield gen.Task(self.db.execute, sqlQuery)
            
            for record in cur:
                [firsttask, chunk] = record
            
            # Now build the query
            [sgeid, sqlQuery] = self.buildQueryOneTask(jobNo, taskNo, firsttask,
                                                       chunk, goodCount)
        
        command = str(self.shellCmdsLocation + "qmod -cj " + sgeid)
        
        # ASync run the two tasks
        dbResult, shellOut = yield [
            gen.Task(self.db.execute, sqlQuery),
            gen.Task(call_subprocess, self, command)
        ]
        
        # Return some JSON saying done.
        # TODO: Check the return values for errors
        output = json.dumps({"sgeid": sgeid})
        self.write(output)
        self.finish()
    
    
    def buildQueryOneTask(self, jobNo, taskNo, firsttask, chunk, goodCount):
        # Using the firsttask and batch size from above, work out the batch
        # starter
        frameNum = int(taskNo)
        fTaskNum = int(firsttask)
        cNum = int(chunk)
        batchNumber = frameNum - (frameNum - fTaskNum) % cNum
        
        # Now decrease donetasks by the size of a batch
        sqlQuery = "UPDATE jobs SET endtime = NULL, donetasks=(donetasks-chunk)"
        sqlQuery += " WHERE sgeid=" + jobNo + "; "
        # If this was the only errored batch then nothing else is still running
        # so set the job as pending, otherwise, leave it as errored
        sqlQuery += "UPDATE jobs SET status = 0 WHERE donetasks="
        sqlQuery += str(goodCount) + " AND sgeid=" + jobNo + "; "
        # and reset the tasks in that batch
        sqlQuery += "UPDATE tasks SET starttime = NULL, endtime = NULL, "
        sqlQuery += "returncode = NULL, rhost = NULL WHERE sgeid=" + jobNo
        sqlQuery += " AND taskno>=" + str(batchNumber) + " AND taskno<"
        sqlQuery += str(batchNumber + cNum) +"; "
        # Build an sgeid reflecting the batch starter instead of the given task
        sgeid = jobNo + "." + str(batchNumber)
        
        return [sgeid, sqlQuery]
    
    
    def buildQueryWholeJob(self, jobNo, goodCount):
        # First set the status to pending if all the tasks have been attempted
        sqlQuery = "UPDATE jobs SET status = 0 WHERE sgeid=" + jobNo + " AND "
        sqlQuery += "donetasks = (lasttask - firsttask + 1); "
        # or set it to running if not all tasks have been attempted
        sqlQuery += "UPDATE jobs SET status = 1 WHERE sgeid=" + jobNo + " AND "
        sqlQuery += "donetasks != (lasttask - firsttask + 1); "
        
        # Now decrease donetasks by that number and set endtime NULL
        sqlQuery += "UPDATE jobs SET endtime = NULL, donetasks=("
        sqlQuery += str(goodCount) + ") WHERE sgeid=" + jobNo + "; "
        # Also, reset any tasks that don't have returncode 0
        sqlQuery += "UPDATE tasks SET starttime = NULL, endtime = NULL, "
        sqlQuery += "returncode = NULL, rhost = NULL WHERE sgeid=" + jobNo
        sqlQuery += " AND returncode != 0;"
        
        return sqlQuery