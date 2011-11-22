from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

#
# Is using cat in here really the best way to do it?
# TODO: Find a better way that streams the file as it's written.
#

class ReadLog(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        sgeid = self.get_argument("sgeid")
        frame = self.get_argument("frame")
        
        # Detemine the first frame of the batch as that'll have the logs
        sqlQuery = "SELECT firsttask, chunk, stdout, stderr FROM jobs "
        sqlQuery += "WHERE sgeid = " + sgeid + ";"
        
        cur = yield gen.Task(self.db.execute, sqlQuery)
        
        for record in cur:
            [firsttask, chunk, stdout, stderr] = record
        
        if stdout is None:
            stdoutReturn = "No stdout path specified"
        if stderr is None:
            stderrReturn = "No stderr path specified"
        
        if stderr is not None and stderr is not None:
            # Logs are only recorded by the first task in a batch
            # The maths below works out what that batchNumber is
            frameNum = int(frame)
            fTaskNum = int(firsttask)
            cNum = int(chunk)
            batchNumber = str(frameNum - (frameNum - fTaskNum) % cNum)
            
            # Build the real filenames
            soFilename = stdout + "." + batchNumber
            seFilename = stderr + "." + batchNumber
            
            # Stdout
            try:
                response = yield gen.Task(call_subprocess, self,
                                          "cat " + soFilename)
                # When the command returns, split the lines and parse them
                theOutput = response.read()
                stdoutReturn = theOutput.replace("\n","<br />\n")
            except IOError as e:
                stdoutReturn = "No stdout"
            
            # Stderr
            try:
                response = yield gen.Task(call_subprocess, self,
                                          "cat " + seFilename)
                # When the command returns, split the lines and parse them
                theOutput = response.read()
                stderrReturn = theOutput.replace("\n","<br />\n")
            except IOError as e:
                stderrReturn = "No stderr"
            
        output = json.dumps({"stdout":stdoutReturn, "stderr":stderrReturn})
        
        self.write(output)
        self.finish()