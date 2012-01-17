from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class QuotaHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        qParam = self.get_argument("queue", "farm.q")
        whichQueue = qParam.encode()
        # Try to get it from memcache first
        output = self.mc.get("theQ-quotas-" + whichQueue)
        # If it's not there, run the shell commmand to get it
        if not output:
            command = self.shellCmdsLocation + "qquota-all -q " + whichQueue
            response = yield gen.Task(call_subprocess, self, command)
            # When the command returns, split the lines and parse them
            theOutput = response.read()
            outputList = theOutput.splitlines()
            
            userRows = []
            for line in outputList:
                if "slots" not in line:
                    continue
                items = line.split()
                
                slot_use = items[1]
                slot_use_right = slot_use.split("=")[1]
                slots_used = slot_use_right.split("/")[0]
                username = items[3]
                
                toAppend = {"username": username, "slots_used": slots_used}
                userRows.append(toAppend)
            output = json.dumps({"rows": userRows})
            # Set it in memcache
            self.mc.set("theQ-quotas-" + whichQueue, output, self.cacheDuration)
        # Write out the output, whether it came from memcache or the shell cmd
        self.write(output)
        self.finish()