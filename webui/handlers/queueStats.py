from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json

import logging
logger = logging.getLogger('theq2.' + __name__)

class QueueStatsHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        qParam = self.get_argument("queue", "farm.q")
        whichQueue = qParam.encode()
        # Try to get it from memcache first
        output = self.mc.get("theQ-queueStats-" + whichQueue)
        # If it's not there, run the shell commmand to get it
        if not output:
            command = self.shellCmdsLocation + "qstat -g c -q " + whichQueue
            response = yield gen.Task(call_subprocess, self, command)
            # When the command returns, split the lines and parse them
            theOutput = response.read()
            outputList = theOutput.splitlines()
            
            used = 0
            avail = 0
            total = ""
            usedpc = 0
            availpc = 0
            broken = 0
            brokenpc = 0
            suspended = 0
            
            for line in outputList:
                if whichQueue not in line:
                    continue
                items = line.split()
                used = int(items[2])
                suspended = int(items[6])
                avail = int(items[4])
                total = int(items[5])
                broken = int(items[7])
                
                good = total - broken - suspended
                goodpc = (float(good) / float(total)) * 100.0
                
                if used != 0:
                    usedpc = (float(used) / float(good)) * 100.0
                else:
                    usedpc = 0.0
                if broken != 0:
                    brokenpc = (float(broken) / float(total)) * 100.0
                else:
                    brokenpc = 0.0
                if suspended != 0:
                    suspendedpc = (float(suspended) / float(total)) * 100.0
                else:
                    suspendedpc = 0.0
                if avail != 0:
                    availpc = (float(avail) / float(good)) * 100.0
                else:
                    availpc = 0.0
                
                usedpc = "%.1f" % usedpc
                availpc = "%.1f" % availpc
                brokenpc = "%.1f" % brokenpc
                suspendedpc = "%.1f" % suspendedpc
                goodpc = "%.1f" % goodpc
                
                # Then create a JSON output from it
                output = json.dumps({"total":total, "used":used,
                                     "avail":avail, "usedpc":usedpc,
                                     "availpc": availpc, "broken":broken,
                                     "brokenpc":brokenpc, "good":good,
                                     "goodpc":goodpc, "suspended":suspended,
                                     "suspendedpc":suspendedpc})
                # and set it in memcache
                self.mc.set("theQ-queueStats-" + whichQueue, output,
                       self.cacheDuration)
        # Write out the output, whether it came from memcache or the shell cmd
        self.write(output)
        self.finish()
