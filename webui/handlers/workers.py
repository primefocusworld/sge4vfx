from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess
import simplejson as json
import re

import logging
logger = logging.getLogger('theq2.' + __name__)

class WorkersHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        # Get all the supplied params
        qParam = self.get_argument("queue", "farm.q")
        whichQueue = qParam.encode()
        # Try to get it from memcache first
        output = self.mc.get("theQ-workers-" + whichQueue)
        # If it's not there, run the shell commmand to get it
        if not output:
            output = ""
            machineRows = []
            
            command = self.shellCmdsLocation + "qstat -f -q " + whichQueue
            response = yield gen.Task(call_subprocess, self, command)
            # When the command returns, split the lines and parse them
            theOutput = response.read()
            outputList = theOutput.splitlines()
            pattern = re.compile(r"" + whichQueue + "@(.*)")
            for line in outputList:
                if whichQueue not in line:
                    continue
                items = line.split()
                
                # Get the name of the machine
                m = pattern.match(items[0])
                fqdn = m.group(1)
                shortName = fqdn.split(".")[0]
                
                [res, used, total] = items[2].split("/")
                res = int(res)
                used = int(used)
                total = int(total)
                
                # If the machine doesn't have a load, say so
                if items[3] != "-NA-":
                    loadAvg = float(items[3])
                else:
                    loadAvg = "NA"
                
                # Work out how full the machine is
                pcused = "%d" % ((float(used) / float(total)) * 100.0)
                if len(items) > 5:
                    machineStates = items[5]
                    if machineStates.find("u") != -1:
                        status = "error"
                    else:
                        status = "warning"
                    pcused = ""
                else:
                    status = ""
                    machineStates = ""
                
                toAppend = {"hostname": shortName, "used": used, "total": total,
                            "pcused": pcused, "load_avg": loadAvg,
                            "machine_states": machineStates, "status": status}
                machineRows.append(toAppend)
            output = json.dumps({"rows": machineRows})
            # Set it in memcache
            self.mc.set("theQ-workers-" + whichQueue, output,
                        self.cacheDuration)
        # Write out the output, whether it came from memcache or the shell cmd
        self.write(output)
        self.finish()