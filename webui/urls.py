from handlers.simple import IndexHandler
from handlers.jobs import MainJobTable
from handlers.shelltest import ShellHandler
from handlers.queueStats import QueueStatsHandler

url_patterns = [
    (r"/", IndexHandler),
    (r"/jobs", MainJobTable),
    (r"/shell", ShellHandler),
    (r"/queueStats", QueueStatsHandler),
]
