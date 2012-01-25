from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json
import re

import logging
logger = logging.getLogger('theq2.' + __name__)

class ResourceHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Try to get it from memcache first
        output = self.mc.get("theQ-resource")
        # If it's not there, run the shell commmand to get it
        if not output:
            command = self.shellCmdsLocation + "get-res"
            response = yield gen.Task(call_subprocess, self, command)
            # When the command returns, split the lines and parse them
            theOutput = response.read()
            outputList = theOutput.splitlines()
            
            resourceRows = []
            for line in outputList:
                line = re.sub(r'\s', '', line)
                preItems = line.split(":")[1]
                items = preItems.split("=")
                
                resName = items[0]
                resAvail = items[1]
                
                toAppend = {"resource": resName, "available": resAvail}
                resourceRows.append(toAppend)
            output = json.dumps({"rows": resourceRows})
            # Set it in memcache
            self.mc.set("theQ-resource", output, self.cacheDuration)
        # Write out the output, whether it came from memcache or the shell cmd
        self.write(output)
        self.finish()
