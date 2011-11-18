from handlers.base import BaseHandler

import tornado.web
from tornado import gen
from async_process import call_subprocess

import logging
logger = logging.getLogger('theq2.' + __name__)


class ShellHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        self.write("Before sleep<br />")
        self.flush()
        response = yield gen.Task(call_subprocess, self, "shell_cmds/qstat -g c -q farm.q")
        theOutput = response.read()
        outputList = theOutput.splitlines()
        for line in outputList:
            self.write(line + "<br />")
        self.finish()
