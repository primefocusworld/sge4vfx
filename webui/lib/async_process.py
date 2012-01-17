# Adapted from here: https://gist.github.com/489093
# Original credit goes to pplante and copyright notice pasted below

# Copyright (c) 2010, Philip Plante of EndlessPaths.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Modifications Copyright (c) 2011, Stephen Willey of cerealkillers.co.uk
# License remains as above
# Modifications allow it to be included once in multiple handlers.  Save it
# as async_process.py and put it in the path somewhere.  Use it like this:
#
# from handlers.base import BaseHandler
# 
# import tornado.web
# from tornado import gen
# from async_process import call_subprocess, on_subprocess_result
# 
# class ShellHandler(BaseHandler):
#     @tornado.web.asynchronous
#     @gen.engine
#     def get(self):
#         self.write("Before sleep<br />")
#         self.flush()
#         response = yield gen.Task(call_subprocess, self, "ls /")
#         self.write("Output is:\n%s" % (response.read(),))
#         self.finish()
#

import logging
import shlex
import subprocess
import tornado

def call_subprocess(context, command, callback=None):
    context.ioloop = tornado.ioloop.IOLoop.instance()
    context.pipe = p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    context.ioloop.add_handler(p.stdout.fileno(), context.async_callback(on_subprocess_result, context, callback), context.ioloop.READ)

def on_subprocess_result(context, callback, fd, result):
    try:
        if callback:
            callback(context.pipe.stdout)
    except Exception, e:
        logging.error(e)
    finally:
        context.ioloop.remove_handler(fd)
