from handlers.simple import IndexHandler
from handlers.jobs import MainJobTable
from handlers.shelltest import ShellHandler

url_patterns = [
    (r"/", IndexHandler),
    (r"/jobs", MainJobTable),
    (r"/shell", ShellHandler),
]
